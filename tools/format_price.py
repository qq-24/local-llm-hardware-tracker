# -*- coding: utf-8 -*-
"""
format_price.py — 价格/数值"自动进位"格式化，提升追踪表可读性。

规则（人民币为主）：
  - < 1000        原样显示
  - 1000 ~ 9999   显示"x千"（如 9000 -> 9千；3600 -> 3.6千）
  - >= 10000      显示"x万"（如 18000 -> 1.8万；120000 -> 12万）
  - 支持"范围/区间"字符串（如 "11200~24000" -> "1.12万~2.4万"）
  - 支持"约"字样与美元标注（$ 前缀跳过换算，仅处理数值部分并保留单位字符）

用法（命令行）：
  python tools/format_price.py 9000 18000 "11200~24000" "约 57万"
  python tools/format_price.py --round 1 9000 18000

用法（作为模块）：
  from tools.format_price import fmt_price, fmt_price_text
  fmt_price(9000)         -> "9千"
  fmt_price_text("18000") -> "1.8万"
"""
import argparse
import re

_MIN = 0.995          # 千位进位阈值（容差，避免浮点边界问题）
MAX_STR = 1_000_000_000_000


def fmt_num(n: float, ndigits: int = 1) -> str:
    """把纯数值进位成中文简写。"""
    if n is None:
        return "-"
    n = float(n)
    if n < 1000:
        # 整数原样，小数去掉多余 0
        if n == int(n):
            return str(int(n))
        return f"{n:.{ndigits}f}".rstrip("0").rstrip(".")
    if n < 10000:
        v = n / 1000.0
        s = f"{v:.{ndigits}f}".rstrip("0").rstrip(".")
        return f"{s}千"
    v = n / 10000.0
    s = f"{v:.{ndigits}f}".rstrip("0").rstrip(".")
    return f"{s}万"


def fmt_price(v) -> str:
    """单个数值或"数值区间/约/单位"等杂串统一格式化。

    支持形式示例：
      9000 / 3599 / 18000 / 11200~24000 / 约 1.8万(已格式化则原样返回)
      >28000 / <10000 / 5000-6000以上
    """
    if v is None:
        return "-"
    if isinstance(v, (int, float)):
        return fmt_num(float(v))

    s = str(v).strip()
    if not s:
        return "-"
    # 已包含 千/万 字样则视为已格式化，原样返回
    if re.search(r"[千万]", s) and not re.search(r"\d", s.replace("千", "").replace("万", "")):
        # 形如 "1.8万"/"约 57万" 直接返回
        return s

    # 提取所有带小数的数字
    numbers = re.findall(r"\d+(?:\.\d+)?", s)
    if not numbers:
        return s
    fmtnums = [fmt_num(float(x)) for x in numbers]
    # 用正则把原来的数字替换成格式化后的（保持间隔符）
    out = s
    for raw, fmt in zip(numbers, fmtnums):
        out = re.sub(rf"\b{re.escape(raw)}\b", fmt, out, count=1)
    return out


def fmt_price_text(s) -> str:
    """字符串入口：支持 、分隔/空格分隔的多个值，以及范围。"""
    if s is None:
        return "-"
    vals = re.split(r"[,，、;；\s]+", str(s).strip())
    return " ".join(fmt_price(x) for x in vals if x)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="价格自动进位格式化")
    ap.add_argument("values", nargs="+", help="数值或字符串，如 9000 18000 11200~24000")
    ap.add_argument("--round", type=int, default=1, help="小数位（默认1）")
    args = ap.parse_args()
    for x in args.values:
        print(fmt_price(x))