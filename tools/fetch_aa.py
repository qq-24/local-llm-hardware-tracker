# -*- coding: utf-8 -*-
"""
fetch_aa.py — 从 Artificial Analysis 抓取 LLM Leaderboard 全表，
按项目标准筛选"当期目标模型"：
  - open weights
  - 进内存总参 <= 250B（以 AA 报告的 totalParameters 为准）
  - 激活 <= 30B
  - AA Intelligence Index 最高者 = Top1

用法：
  python tools/fetch_aa.py                          # 自动判定，保存快照到 版本快照/aa-target.<日期>.md
  python tools/fetch_aa.py --no-save                # 只打印不保存
  python tools/fetch_aa.py --model "Qwen3.8-Flash-Next"  # 手动指定覆盖
  python tools/fetch_aa.py --max-total 250 --max-active 30

数据源：https://artificialanalysis.ai/leaderboards/models
页面为 Next.js RSS，模型数组作为 React 组件 props("models") 内嵌在 __next_f chunk 字符串中。
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.request

LEADERBOARD_URL = "https://artificialanalysis.ai/leaderboards/models"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
INDEX_KEYS = ["artificialAnalysisIntelligenceIndex", "intelligenceIndex"]
MARKER = "self.__next_f.push("


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", "ignore")


def find_models_chunk(html_text):
    """遍历 __next_f push 数组，解码每块字符串，返回包含 'totalParameters' 的最长块内容。"""
    dec = json.JSONDecoder()
    pos = 0
    best, best_len = None, 0
    while True:
        i = html_text.find(MARKER, pos)
        if i == -1:
            break
        try:
            obj, _ = dec.raw_decode(html_text[i + len(MARKER):])
        except Exception:
            pos = i + len(MARKER)
            continue
        content = obj[1] if len(obj) > 1 and isinstance(obj[1], str) else None
        if content and "totalParameters" in content and len(content) > best_len:
            best, best_len = content, len(content)
        pos = i + len(MARKER)
    if best is None:
        raise RuntimeError("未找到含模型数据的 chunk")
    return best


def extract_models_array(content):
    """在解码后的 chunk 内容里，定位 'models':[ 并配平取出数组 JSON 文本。"""
    m = content.find('"models"')
    if m == -1:
        # 可能无引号形式
        m = content.find("models")
    # 找到冒号后的 '['
    idx = content.find('[', m)
    # 配平
    depth = 0
    in_str = False
    i = idx
    n = len(content)
    while i < n:
        c = content[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            if c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    return content[idx:i + 1]
        i += 1
    raise RuntimeError("models 数组括号不配平")


def parse_models(html_text):
    chunk = find_models_chunk(html_text)
    arr_text = extract_models_array(chunk)
    return json.loads(arr_text), len(chunk)


def get_intel(d):
    for k in INDEX_KEYS:
        v = d.get(k)
        if isinstance(v, dict):
            v = v.get("value")
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--max-total", type=float, default=250.0)
    ap.add_argument("--max-active", type=float, default=30.0)
    args = ap.parse_args()

    print("抓取 AA leaderboard ...")
    html_text = fetch(LEADERBOARD_URL)
    print(f"HTML: {len(html_text)/1e6:.1f} MB")

    arr, chunk_len = parse_models(html_text)
    print(f"模型数组: {len(arr)} 个（chunk {chunk_len/1e6:.2f} MB）")
    if len(arr) < 100:
        raise RuntimeError(f"模型过少({len(arr)})，页面结构可能变化")

    rows = []
    for d in arr:
        rows.append({
            "slug": d.get("slug") or "",
            "name": d.get("shortName") or d.get("name") or d.get("slug") or "?",
            "total": d.get("totalParameters"),
            "active": d.get("activeParameters"),
            "open": bool(d.get("isOpenWeights") or d.get("openWeights") or d.get("isOpen")),
            "index": get_intel(d),
            "context": d.get("contextWindowTokens"),
            "hf": d.get("huggingfaceUrl") or "",
            "speed": d.get("medianOutputTokensPerSecond") or d.get("medianTokensPerSecond"),
            "cost": d.get("price1mBlended0To3To1"),
            "license": d.get("licenseName") or "",
            "creator": d.get("modelCreatorName") or (d.get("creator") or {}).get("name", ""),
        })

    cand = [r for r in rows
            if r["open"] and r["total"] is not None and r["active"] is not None
            and 0 < r["total"] <= args.max_total and 0 < r["active"] <= args.max_active
            and r["index"] is not None]
    cand.sort(key=lambda r: -(r["index"] or 0))

    print(f"\n满足 open weights + total≤{args.max_total:.0f}B + active≤{args.max_active:.0f}B 候选: {len(cand)}")
    if not cand:
        print("!! 无候选"); sys.exit(1)

    top = cand[0]
    print("\nTop 10 候选:")
    for i, r in enumerate(cand[:10], 1):
        flag = "  <== Top" if i == 1 else ""
        print(f"{i}. {r['name']:40s} AA={r['index']:5.1f} total={r['total']:6.0f}B "
              f"active={r['active']:3.0f}B ctx={r['context']} speed={r['speed']}{flag}")

    target, mode = top, "auto"
    if args.model:
        q = args.model.lower()
        target = next((r for r in rows if r["name"].lower() == q or r["slug"].lower() == q), None)
        if not target:
            print(f"!! 手动指定模型未找到: {args.model}")
            sys.exit(2)
        mode = "manual"
        print(f"\n手动指定: {target['name']}  AA={target['index']}")

    if args.no_save:
        return

    now = dt.date.today().isoformat()
    out = args.out or f"版本快照/aa-target.{now}.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# AA 目标模型快照（{now}）\n\n")
        f.write(f"- 抓取源: {LEADERBOARD_URL}\n")
        f.write(f"- 筛选: open weights / total≤{args.max_total:.0f}B / active≤{args.max_active:.0f}B\n")
        f.write(f"- 模式: {mode}\n\n")
        f.write("| # | 模型 | Creator | AA智力 | 总参(B) | 激活(B) | 上下文 | 速度t/s | 价格$/M |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
        for i, r in enumerate(cand[:10], 1):
            mark = "**" if r is target else ""
            f.write(f"| {i} | {mark}{r['name']}{mark} | {r['creator']} | {r['index']:.1f} | "
                    f"{r['total']:.0f} | {r['active']:.0f} | {r['context']} | "
                    f"{r['speed'] if r['speed'] is not None else '-'} | "
                    f"{r['cost'] if r['cost'] is not None else '-'} |\n")
        f.write(f"\n**当期目标: {target['name']}（AA={target['index']:.1f}, "
                f"total={target['total']:.0f}B, active={target['active']:.0f}B）**\n")
        if target["hf"]:
            f.write(f"HF: {target['hf']}\n")
    print(f"\n已保存: {out}")


if __name__ == "__main__":
    main()