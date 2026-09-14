#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Times CAR 数据的持久化快照（data/snapshot.md）读写。

快照是**唯一的数据源**：mail/*.eml 与 site/*.csv 由 ingest.py 并入本文件后即可删除，
之后 parse_mail.py 只从本文件读取。

文件结构：三个 markdown 表格小节
    ## bookings   预约邮件（予約登録/変更完了）
    ## returns    返却証（実績 + 驾驶行为）
    ## csv        官网导出的利用明细

约定：
- 键为 `予約番号`（bookings/returns）与「予約開始日時 + ステーション」（csv）
- 重复数据后覆盖前，因此**幂等**：同一批数据反复并入结果一致
"""

import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
SNAPSHOT = os.path.join(DATA_DIR, "snapshot.md")

# 三个表的列（顺序即写出顺序；读取时按表头对齐，加列不会破坏旧快照）
BOOK_COLS = ["予約番号", "ステーション", "車両", "利用開始日時", "返却予定日時"]
RETURN_COLS = [
    "予約番号", "ステーション", "車両", "予約時間", "利用時間", "走行距離",
    "最高速度", "急加速回数", "急減速回数",
    "時間料金", "距離料金", "ペナルティ金額", "安心補償サービス", "合計金額",
]
CSV_COLS = [
    "予約開始日時", "返却予定日時", "利用開始日時", "利用終了日時",
    "ステーション", "利用時間", "走行距離", "請求金額",
]

SECTIONS = [("bookings", BOOK_COLS), ("returns", RETURN_COLS), ("csv", CSV_COLS)]


# ---------------- 读 ----------------
def _split_sections(text):
    """按 `## 小节名` 切分，返回 {name: [lines]}。"""
    sections, cur, buf = {}, None, []
    for ln in text.splitlines():
        if ln.startswith("## "):
            if cur is not None:
                sections[cur] = buf
            cur = ln[3:].strip()
            buf = []
        else:
            buf.append(ln)
    if cur is not None:
        sections[cur] = buf
    return sections


def _table_rows(lines, columns):
    """解析 markdown 表格，返回 list[dict]。表头需以 columns[0] 开头。"""
    header, out = None, []
    for ln in lines:
        s = ln.strip()
        if not s.startswith("|"):
            if header:
                break  # 表格结束
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            if cells and cells[0] == columns[0]:
                header = cells
            continue
        if set("".join(cells)) <= set("- "):
            continue
        if len(cells) != len(header):
            continue
        out.append(dict(zip(header, cells)))
    return out


def _rows_to_dict(rows, key="予約番号"):
    rows = rows or []
    return {r[key]: r for r in rows if (r.get(key) or "").strip()}


def load_snapshot(path=SNAPSHOT):
    """返回 (books: dict, returns: dict, csv_rows: list[dict])。文件不存在返回空。"""
    if not os.path.isfile(path):
        return {}, {}, []
    text = open(path, encoding="utf-8").read()
    sections = _split_sections(text)
    books = _rows_to_dict(_table_rows(sections.get("bookings", []), BOOK_COLS))
    returns = _rows_to_dict(_table_rows(sections.get("returns", []), RETURN_COLS))
    csv_rows = _table_rows(sections.get("csv", []), CSV_COLS)
    return books, returns, csv_rows


# ---------------- 写 ----------------
def _md_table(title, columns, rows):
    lines = ["", f"## {title}", ""]
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
    for r in rows:
        cells = [str(r.get(c, "") or "").replace("|", "／").replace("\n", " ") for c in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def save_snapshot(books, returns, csv_rows, path=SNAPSHOT):
    """写快照。三个集合都按键去重后按主键排序，保证输出稳定（便于 diff）。"""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def sorted_rows(d, key="予約番号"):
        return [d[k] for k in sorted(d, key=lambda x: str(x))]

    def csv_sorted(rows):
        return sorted(rows, key=lambda r: (r.get("予約開始日時", ""), r.get("ステーション", "")))

    lines = [
        "# Times CAR 数据快照",
        "",
        "> **自动生成，请勿手工编辑**。由 `ingest.py` 维护：把 `mail/*.eml`、`site/*.csv`",
        "> 并入本文件后，原始数据即可删除。重复并入是幂等的（后覆盖前）。",
        "",
        f"- 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 预约 {len(books)} 条 / 返却証 {len(returns)} 条 / CSV 明细 {len(csv_rows)} 条",
    ]
    lines += _md_table("bookings", BOOK_COLS, sorted_rows(books))
    lines += _md_table("returns", RETURN_COLS, sorted_rows(returns))
    lines += _md_table("csv", CSV_COLS, csv_sorted(csv_rows))

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path
