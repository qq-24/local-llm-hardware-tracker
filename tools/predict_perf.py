# -*- coding: utf-8 -*-
"""
predict_perf.py — 本地大模型推理性能【纯推算】引擎（不依赖实测）。

核心公式链（每步可复核，所有输出标 [推算]）：
  decode_t/s = 内存带宽(GB/s) × 利用率(0.8) ÷ 每token读取字节(GB)
    每token读取 = 激活参数(B) × 1.3(路由开销) × 量化字节(Q4=0.5)
                + KV每token字节 × 上下文 × 0.25(KV读占比@长上下文)

  prefill_t/s = 算力(TFLOPS FP16含Tensor) × 0.8 ÷ 每token计算量(GFLOPs)
    每token计算量 = 2 × 激活参数(十亿)  GFLOP

  多卡并行效率（TS并行, 按卡间互联带宽）:
    r = 卡间带宽(GB/s) ÷ 单卡内存带宽(GB/s)
    eff_multi = N / (1 + (N-1) × 0.3 / r)     # k=0.3 经验常数

  C2 判定: decode ≷ 50 t/s；C3 判定: prefill ≷ 1500 t/s

用法:
  python tools/predict_perf.py --model qwen3.8-flash-next --ctx 1000000
  python tools/predict_perf.py --model qwen3.8-flash-next --ctx 1000000 --only CMP_170HX,M5_Ultra
"""
import argparse
import json
import math
import os

UTIL = 0.8              # 利用率（固定）
ROUTE_OVERHEAD = 1.3    # MoE 路由开销系数
KV_READ_FRAC = 0.25     # 长上下文 KV 读占比
MULTI_K = 0.3           # 多卡 TS 并行经验常数
C2 = 50.0
C3 = 1500.0

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = os.path.join(TOOLS_DIR, "hw_specs.json")

# 模型参数表：来自官方 config.safetensors 实测（版本快照/01-模型档案）
MODELS = {
    "qwen3.8-flash-next": {
        "name": "Qwen3.8-Flash-Next",
        "active_params_b": 6.0,        # 激活参数(B)
        "total_params_b": 180.0,       # 总参(含n-gram, 供参考)
        "kv_bytes_per_token": 12288.0, # KV Q8 每token字节(12层×2KV头×256×2)
    },
}


def fmt(t, nd=1):
    if t is None:
        return "-"
    return f"{t:.{nd}f}"


def decode_tps(bw_gb_s, active_b, kv_ptoken, ctx, n=1, eff=1.0):
    """decode 出字速度 t/s（带宽墙）。
    每token读取字节 = 激活权重(Q4) + KV读占。"""
    w_gb = active_b * ROUTE_OVERHEAD * 0.5 * 1e9          # 激活权重Q4 字节/token
    kv_gb = kv_ptoken * ctx * KV_READ_FRAC                 # KV读取字节/token
    total_bytes = w_gb + kv_gb
    return bw_gb_s * 1e9 * UTIL / total_bytes * eff


def prefill_tps(tflops, active_b, eff=1.0):
    """prefill 速度 t/s（算力墙）。"""
    if tflops is None:
        return None
    flops_per_tok_g = 2.0 * active_b * 1e9        # FLOP/token
    return tflops * 1e12 * UTIL / flops_per_tok_g * eff


def multi_eff(n, inter_bw, mem_bw):
    """TS 并行多卡效率放大倍数（相对单卡），封顶 = N。
    通信开销按 r=卡间带宽/内存带宽；r 越大越接近线性。"""
    if n <= 1 or inter_bw <= 0:
        return 1.0
    r = inter_bw / mem_bw if mem_bw else 0
    if r <= 0:
        return 1.0
    eff = n / (1 + (n - 1) * MULTI_K / r)
    return min(eff, n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3.8-flash-next")
    ap.add_argument("--ctx", type=int, default=1000000)
    ap.add_argument("--only", default=None, help="逗号分隔的硬件名，如 'CMP_170HX,M5_Ultra'")
    ap.add_argument("--json", action="store_true", help="输出 JSON 方便入库")
    args = ap.parse_args()

    if args.model not in MODELS:
        raise SystemExit(f"未知模型 {args.model}，可选: {list(MODELS)}")
    m = MODELS[args.model]

    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        specs = json.load(f)
    headers, data = specs["说明"], specs

    # 方案清单（硬件 × 卡数）
    plans = [
        ("V100_32G", 3), ("V100_32G", 4),
        ("CMP_170HX", 1), ("CMP_170HX", 2),
        ("RTX_4090", 1),
        ("Strix_Halo_395", 1),
        ("M5_Max_128G", 1),
        ("M5_Ultra", 1),
    ]
    if args.only:
        only = dict((s.split(":")[0], int(s.split(":")[1])) for s in args.only.split(",") if ":" in s)
        plans = [(k, v) for k, v in plans if k in only]
        if not plans:
            plans = [(s, 1) for s in args.only.split(",")]

    rows = []
    for hw_name, n in plans:
        if hw_name not in specs or not isinstance(specs[hw_name], dict):
            continue
        h = specs[hw_name]
        mem_bw = h.get("mem_bw")
        tflops = h.get("fp16_tflops")
        inter_bw = h.get("inter_bw", 0.0)
        eff = multi_eff(n, inter_bw, mem_bw if mem_bw else 0)   # 放大倍数(相对单卡), ≤N
        comm_frac = (eff / n) if n > 1 else 1.0                 # 通信效率 0~1
        dec = decode_tps(mem_bw, m["active_params_b"], m["kv_bytes_per_token"], args.ctx, n, eff)
        pre = prefill_tps(tflops, m["active_params_b"], eff) if tflops is not None else None
        rows.append({
            "hw": hw_name, "n": n, "pcie": h.get("pcie"),
            "mem_bw_total": mem_bw * n,
            "decode_tps": dec, "prefill_tps": pre,
            "c2_pass": dec >= C2, "c3_pass": (pre >= C3 if pre is not None else None),
            "comm_frac": comm_frac, "note": h.get("备注", ""),
        })

    # 排序：先显示能过 C1 装得下的方案，按 decode 降序（本文只算速度，装不装得下另表）
    rows.sort(key=lambda r: -(r["decode_tps"] or 0))

    print(f"模型: {m['name']}  激活 {m['active_params_b']}B  KV每token {m['kv_bytes_per_token']}B/{(m['kv_bytes_per_token']/1e9*args.ctx):.1f}GB@ctx")
    print(f"固定利用率 {UTIL} | 路由系数 {ROUTE_OVERHEAD} | KV读占比 {KV_READ_FRAC} | 多卡k {MULTI_K}")
    print(f"C2≥{C2} t/s | C3≥{C3} t/s （全部为 [推算]，非实测）\n")

    hdr = f"{'硬件':<14}{'卡':<3}{'通信效率':<8}{'总带宽GB/s':<11}{'decode t/s':<11}{'C2':<4}{'prefill':<10}{'C3'}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        c3s = "✅" if r["c3_pass"] is True else ("❌" if r["c3_pass"] is False else "-")
        print(f"{r['hw']:<14}{r['n']:<3}{r['comm_frac']:<8.2f}"
              f"{r['mem_bw_total']:<11.1f}{fmt(r['decode_tps']):<11}C2={'✅' if r['c2_pass'] else '❌'}  "
              f"{fmt(r['prefill_tps']):<10}{c3s}")

    if args.json:
        print()
        print(json.dumps({"model": m["name"], "ctx": args.ctx, "rows": rows}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()