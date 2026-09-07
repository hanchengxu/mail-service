"""楽天証券「投信基準価額メール」解析器：统计今日盈亏。

用法：
    # 1) 由 run_tasks.py 自动调用：tasks.yml 里给任务配 actions，脚本从 stdin 收到上一步输出
    actions:
      - actions/rakuten-sec-action.py

    # 2) 单独使用
    python imap_qq_test.py "楽天証券" -t "投信基準価額" --all -n 1 | python actions/rakuten-sec-action.py
    python actions/rakuten-sec-action.py mail.txt

输出：一行中文结论，例如
    基准日 09月04日｜今日盈亏（各基金1万口换算合计）：-823円（-0.29%）⇒ 亏损

盈亏口径：默认直接把各基金的「前営業日比額」求和，得出今日盈亏（按每支基金各 1 万口换算），
不需要任何配置。若想按实际持仓计算，在 HOLDINGS 里填「ファンド名: 口数(万口)」，
会额外输出一行按持仓的盈亏（基準価額是每 1 万口的价格，故 10.5 表示持有 105,000 口）。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 持有口数（单位：万口）。ファンド名可用部分匹配，写不全也能对上。
HOLDINGS: dict[str, float] = {
    # "eMAXIS Slim 米国株式（S&P500）": 12.5,
    # "eMAXIS Slim 国内株式（TOPIX）": 8.0,
}

# 全角数字/符号 -> 半角
_TRANSLATION = str.maketrans({
    "０": "0", "１": "1", "２": "2", "３": "3", "４": "4",
    "５": "5", "６": "6", "７": "7", "８": "8", "９": "9",
    "％": "%", "＋": "+", "－": "-", "−": "-", "．": ".", "，": ",",
    "　": " ",
})

FUND_PATTERN = re.compile(
    r"(?P<name>[^\n]+?)\s*\n\s*"
    r"\((?P<company>[^)]*)\)\s*\n\s*"
    r"(?P<price>[0-9,]+)\s*円\s*\n?\s*"
    r"(?P<diff>[+-]?[0-9,]+)\s*円\s*\n?\s*"
    r"\(\s*(?P<pct>[+-]?[0-9.]+)\s*%\s*\)\s*\n?\s*"
    r"(?P<ret>[+-]?[0-9.]+)\s*%"
)
DATE_PATTERN = re.compile(r"基準価額は\s*(\d{1,2})月(\d{1,2})日時点")


def normalize(text: str) -> str:
    return text.translate(_TRANSLATION)


def _to_int(text: str) -> int:
    return int(text.replace(",", "").replace("+", ""))


def match_units(name: str) -> float | None:
    """按 HOLDINGS 找持仓口数，支持部分匹配。"""
    for key, units in HOLDINGS.items():
        k = normalize(key).strip()
        if k and (k in name or name in k):
            return units
    return None


def parse(text: str) -> list[dict]:
    text = normalize(text)
    funds = []
    for m in FUND_PATTERN.finditer(text):
        name = m.group("name").strip()
        funds.append(
            {
                "name": name,
                "company": m.group("company").strip(),
                "price": _to_int(m.group("price")),
                "diff": _to_int(m.group("diff")),
                "pct": float(m.group("pct")),
                "return": float(m.group("ret")),
                "units": match_units(name),
            }
        )
    return funds


def reference_date(text: str) -> str:
    m = DATE_PATTERN.search(normalize(text))
    return f"{m.group(1)}月{m.group(2)}日" if m else ""


def report(text: str) -> str:
    funds = parse(text)
    if not funds:
        return "未在输入文本中识别到「投信基準価額メール」的基金数据。"

    # 前営業日比額求和 -> 今日盈亏（按每支基金各 1 万口换算）
    total_price = sum(f["price"] for f in funds)
    total_diff = sum(f["diff"] for f in funds)
    prev_total = total_price - total_diff
    rate = (total_diff / prev_total * 100) if prev_total else 0.0
    verdict = "盈利" if total_diff > 0 else ("亏损" if total_diff < 0 else "持平")

    date = reference_date(text)
    prefix = f"乐天证券 {date}｜" if date else ""
    lines = [
        f"{prefix}盈亏：{total_diff:+,}円（{rate:+.2f}%）⇒ {verdict}"
    ]

    if HOLDINGS:  # 只在配置了持仓时才额外输出按持仓的盈亏
        total_value = total_pl = 0.0
        missing: list[str] = []
        for f in funds:
            if f["units"] is None:
                missing.append(f["name"])
                continue
            total_value += f["price"] * f["units"]
            total_pl += f["diff"] * f["units"]
        prev_value = total_value - total_pl
        holding_rate = (total_pl / prev_value * 100) if prev_value else 0.0
        lines.append(
            f"按持仓合计：市值 {round(total_value):,}円，"
            f"盈亏 {round(total_pl):+,}円（{holding_rate:+.2f}%）"
        )
        if missing:
            lines.append("未计入持仓合计（未配置口数）：" + "、".join(missing))

    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        path = Path(argv[1])
        if not path.is_file():
            print(f"文件不存在：{path}")
            return 1
        text = path.read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()

    print(report(text))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
