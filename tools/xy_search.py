# -*- coding: utf-8 -*-
r"""
xy_search.py — 闲鱼二手显卡行情快速采集器。
复用 ai-goofish-monitor 项目导出过登录态 (xianyu_state.json)，只做搜索->价格基线。

依赖：
  - 环境变量 XY_APP_DIR 指向 ai-goofish-monitor 项目根目录（其中含 xianyu_state.json）
    示例（PowerShell）: $env:XY_APP_DIR="<项目根目录>"
  - 使用该项目的 .venv 解释器运行（内置 playwright）:
      & "$env:XY_APP_DIR\.venv\Scripts\python.exe" .\tools\xy_search.py --keyword "CMP 170HX" --pages 1

用法:
  python tools/xy_search.py --keyword "CMP 170HX" --pages 1
  python tools/xy_search.py --keyword "V100 32G" --pages 2 --out "版本快照/xy-V100.md"

输出: 默认 版本快照/xy-<关键词>.md （价格分位统计表）
说明: 出于隐私，输出不再包含卖家昵称与完整商品链接。
"""
import argparse
import asyncio
import datetime as dt
import json
import os
import statistics
import sys
import urllib.parse

from playwright.async_api import async_playwright

XY_APP_DIR = os.environ.get("XY_APP_DIR", "")
STATE_FILE = os.path.join(XY_APP_DIR, "xianyu_state.json") if XY_APP_DIR else "xianyu_state.json"
SEARCH_API_FRAG = "/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/"
GOOFISH_HOME = "https://www.goofish.com/"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "版本快照")


def parse_price(s):
    """'¥15,800' / '1.5万' -> float 元。"""
    if not s:
        return None
    s = str(s).replace(",", "").replace("¥", "").strip()
    if "万" in s:
        try:
            return float(s.replace("万", "")) * 10000
        except ValueError:
            return None
    if "千" in s:
        try:
            return float(s.replace("千", "")) * 1000
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_search_json(js):
    """搜索接口 resultList -> [{title,price,area,url,itemId,publishTime}]。"""
    items = (js or {}).get("data", {}).get("resultList", []) or []
    rows = []
    for it in items:
        main = (it.get("data", {}).get("item", {}).get("main", {}) or {})
        ex = main.get("exContent", {}) or {}
        click = (main.get("clickParam", {}).get("args", {}) or {})
        price_parts = ex.get("price", []) or []
        price = "".join(p.get("text", "") for p in price_parts if isinstance(p, dict))
        raw_link = main.get("targetUrl", "") or ""
        rows.append({
            "title": ex.get("title", "未知"),
            "price_raw": price,
            "price": parse_price(price),
            "area": ex.get("area", "未知"),
            "seller": ex.get("userNickName", "匿名"),
            "url": raw_link.replace("fleamarket://", "https://www.goofish.com/"),
            "itemId": ex.get("itemId", ""),
            "publishTs": click.get("publishTime", ""),
        })
    return rows


def is_search_response(r):
    req = getattr(r, "request", None)
    return SEARCH_API_FRAG in r.url and getattr(req, "method", None) == "POST"


def fmt_price_fraction(prices, suffix="拳"):
    pass


async def run(keyword, pages):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        snap = json.load(f)
    storage_arg = snap if isinstance(snap, dict) and "cookies" in snap else {"cookies": snap.get("cookies", [])}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="msedge")
        ctx = await browser.new_context(storage_state=storage_arg, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await ctx.new_page()
        # 先访问首页建立会话（反爬）
        await page.goto(GOOFISH_HOME, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(1500)

        search_url = f"https://www.goofish.com/search?q={urllib.parse.quote(keyword)}"
        all_items = []
        cur = 0
        for pageno in range(1, max(1, pages) + 1):
            try:
                if pageno == 1:
                    async with page.expect_response(is_search_response, timeout=30000) as resp_info:
                        await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                    resp = await resp_info.value
                else:
                    btn = page.locator("button[class*='search-pagination-arrow-container']:has([class*='search-pagination-arrow-right']):not([disabled])").first
                    if not await btn.count():
                        break
                    async with page.expect_response(is_search_response, timeout=20000) as resp_info:
                        await btn.click(timeout=10000)
                    await page.wait_for_timeout(2000)
                    resp = await resp_info.value
            except Exception as e:
                print(f"[第{pageno}页] 搜索/翻页失败: {e}", file=sys.stderr)
                break

            js = await resp.json()
            rows = parse_search_json(js)
            print(f"[第{pageno}页] 抓到 {len(rows)} 条")
            all_items.extend(rows)
            if len(rows) < 10:
                break
        await browser.close()

    # 去重
    seen = set()
    deduped = []
    for it in all_items:
        k = it["itemId"] or it["url"]
        if k and k not in seen:
            seen.add(k)
            deduped.append(it)

    prices = [it["price"] for it in deduped if it["price"] is not None and it["price"] > 0]
    return deduped, prices


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyword", required=True)
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if not os.path.exists(STATE_FILE):
        raise SystemExit(f"未找到登录态 {STATE_FILE}\n请先用闲鱼项目 chrome 扩展导出 xianyu_state.json")

    items, prices = asyncio.run(run(args.keyword, args.pages))
    print(f"\n采集 {len(items)} 条(去重后)，有效价格 {len(prices)} 条")

    out = args.out or os.path.join(OUT_DIR, f"xy-{args.keyword.replace(' ', '_')}.{dt.date.today().isoformat()}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# 闲鱼行情快照：{args.keyword}\n\n")
        f.write(f"- 采集时间: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"- 采集方式: xy_search.py（复用已导出登录态）\n\n")
        if prices:
            pmed = statistics.median(prices)
            p25 = sorted(prices)[max(0, len(prices)//4 - 1)]
            p75 = sorted(prices)[min(len(prices)-1, len(prices)*3//4)]
            f.write("### 价格统计（¥）\n\n")
            f.write("| 项 | 值 |\n| --- | --- |\n")
            f.write(f"| 数量 | {len(prices)} |\n")
            f.write(f"| 最低 | {min(prices):.0f} |\n")
            f.write(f"| p25 | {p25:.0f} |\n")
            f.write(f"| 中位 p50 | {pmed:.0f} |\n")
            f.write(f"| p75 | {p75:.0f} |\n")
            f.write(f"| 最高 | {max(prices):.0f} |\n")
            f.write(f"| 均值 | {statistics.mean(prices):.0f} |\n\n")
        f.write("### 商品清单（脱敏：无卖家/链接）\n\n")
        f.write("| 标题 | 价格(¥) | 地区 | 发布时间 |\n|---|---|---|---|\n")
        for it in items:
            pt = it.get("publishTs", "")
            tstr = ""
            if str(pt).isdigit():
                try:
                    tstr = dt.datetime.fromtimestamp(int(pt)/1000).strftime("%Y-%m-%d")
                except Exception:
                    pass
            f.write(f"| {it['title'][:40]} | {it['price_raw']} | {it['area']} | {tstr} |\n")
    print(f"已保存: {out}")


if __name__ == "__main__":
    main()