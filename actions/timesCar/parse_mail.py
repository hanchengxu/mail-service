#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""整合 Times CAR 租车记录 → 输出 formMail.md（9 列，供 build_web.py 使用）。

数据源（按优先级自动降级）：
  1. mail/*.eml 中的「返却証」邮件        → 実績（利用時間 / 走行距離 / 合計金額）+ 驾驶行为
  2. site/*.csv（网站导出的利用明细）     → 実績（仅当该预约没有返却証时兜底）
  3. mail/*.eml 中的「予約登録/変更完了」 → 预约信息（予約番号 / ステーション / 車両）

关联方式：
  - 返却証 与 予約完了 都含「予約番号」→ 直接按键关联（比旧的「时间+站点」稳）。
  - CSV 无「予約番号」列，仍用「预约开始时间 + ステーション」与预约邮件关联。

收录规则：只要有実績（返却証 或 CSV 任一）即收录；同一予約番号有多封邮件时，
按邮件发送时间升序处理、后覆盖前（使「予約変更完了」覆盖「予約登録完了」）。
"""

import csv
import email
import glob
import os
import re
import sys
from datetime import datetime
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIL_DIR = os.path.join(BASE_DIR, "mail")
SITE_DIR = os.path.join(BASE_DIR, "site")
OUT_FILE = os.path.join(BASE_DIR, "formMail.md")

# 预约邮件（予約登録完了 / 予約変更完了）要抓取的字段
MAIL_BOOK_FIELDS = ["予約番号", "ステーション", "車両", "利用開始日時", "返却予定日時"]
# 返却証邮件要抓取的字段
MAIL_RETURN_FIELDS = [
    "予約番号", "ステーション", "車両", "予約時間", "利用時間", "走行距離",
    "最高速度", "急加速回数", "急減速回数",
    "時間料金", "距離料金", "ペナルティ金額", "安心補償サービス", "合計金額",
]
CSV_MAIN_ITEM = "利用料金"


# ---------------- 通用工具 ----------------

def norm_station(s):
    """站点名归一化：去空白、全角空格。"""
    return re.sub(r"[\s　]+", "", s or "")


def norm_datetime(s):
    """'2026年01月30日(金) 11:30' / '2026/01/30 11:30' → '2026-01-30 11:30'。"""
    s = (s or "").strip()
    m = re.search(r"(\d{4})\s*[年/-]\s*(\d{1,2})\s*[月/-]\s*(\d{1,2})\s*日?\s*"
                  r"(?:\([^)]*\))?\s*(\d{1,2}):(\d{2})?", s)
    if m:
        y, mo, d, h, mi = m.groups()
        return "%04d-%02d-%02d %02d:%02d" % (int(y), int(mo), int(d), int(h), int(mi or 0))
    return s


def fmt_slash(s):
    """'2026-01-30 11:30' → '2026/01/30 11:30'（保持 md 原有写法）。"""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})", s or "")
    return "%s/%s/%s %s:%s" % m.groups() if m else (s or "")


def to_int(s):
    """'22km' / '4,510円' / '3,960円（4時間18分）' → 22 / 4510 / 3960。"""
    m = re.search(r"(-?[\d,]+)", s or "")
    if not m:
        return 0
    try:
        return int(m.group(1).replace(",", ""))
    except ValueError:
        return 0


def minutes_to_hm(s):
    """143 → '2時間23分'"""
    try:
        v = int(str(s).strip())
    except (ValueError, TypeError):
        return str(s or "")
    sign = "-" if v < 0 else ""
    v = abs(v)
    return "%s%d時間%d分" % (sign, v // 60, v % 60)


DT_PAT = (r"\d{4}\s*[年/-]\s*\d{1,2}\s*[月/-]\s*\d{1,2}\s*日?\s*"
          r"(?:\([^)]*\))?\s*\d{1,2}:\d{2}")


def parse_range(s):
    """'2026/09/12 13:45 - 2026/09/12 18:03' → ('2026-09-12 13:45','2026-09-12 18:03')。"""
    ms = re.findall(DT_PAT, s or "")
    if len(ms) >= 2:
        return norm_datetime(ms[0]), norm_datetime(ms[-1])
    if len(ms) == 1:
        return norm_datetime(ms[0]), ""
    return "", ""


def diff_minutes(a, b):
    """两个 'YYYY-MM-DD HH:MM' 之间相差的分钟数（不超过 0 则记 0）。"""
    def p(x):
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2}):(\d{2})", x or "")
        return datetime(*map(int, m.groups())) if m else None
    da, db = p(a), p(b)
    if not da or not db:
        return 0
    return max(int((db - da).total_seconds() // 60), 0)


# ---------------- 邮件侧 ----------------

def decode_subject(msg):
    try:
        return str(make_header(decode_header(msg.get("Subject", ""))))
    except Exception:
        return msg.get("Subject", "")


def decode_body(msg):
    """返回邮件纯文本正文（自动处理 charset 与 transfer-encoding）。"""
    parts = []
    candidates = msg.walk() if msg.is_multipart() else [msg]
    for part in candidates:
        if part.get_content_maintype() != "text":
            continue
        if part.get_content_subtype() not in ("plain", "html"):
            continue
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        charset = part.get_content_charset() or "utf-8"
        try:
            parts.append(payload.decode(charset, errors="replace"))
        except LookupError:
            parts.append(payload.decode("utf-8", errors="replace"))
    return "\n".join(parts)


def extract_fields(text, labels):
    """抓取「■标签\\n值」格式的字段（跳过 http 开头的行）。"""
    lines = [ln.rstrip("\r\n").strip() for ln in text.splitlines()]
    data = {}
    for label in labels:
        for i, ln in enumerate(lines):
            if re.match(r"^[■□※◆・]?\s*" + re.escape(label) + r"\s*$", ln):
                for nxt in lines[i + 1:]:
                    if nxt and not nxt.startswith("http"):
                        data[label] = nxt
                        break
                break
    return data


def classify(subject):
    """按标题判断邮件类型：返却証 → 'return'；予約登録/変更完了 → 'book'。"""
    s = subject or ""
    if "返却" in s:
        return "return"
    if "予約" in s and ("登録" in s or "変更" in s or "完了" in s):
        return "book"
    return None


def mail_datetime(msg):
    try:
        return parsedate_to_datetime(msg.get("Date", ""))
    except Exception:
        return None


def load_mails_from_dir():
    """从 `mail/*.eml` 读取（原始邮件目录）。

    返回 (books, returns)：均为 予約番号 -> 字段 dict（按邮件时间升序，后覆盖前）。
    仅供 ingest.py 使用；正式解析走下面的 load_mails()（读快照）。
    """
    files = sorted(glob.glob(os.path.join(MAIL_DIR, "*.eml")))
    if not files:
        print("警告：mail 目录下没有 .eml 文件")

    def by_date(path):
        with open(path, "rb") as f:
            msg = email.message_from_binary_file(f)
        dt = mail_datetime(msg)
        return (dt.timestamp() if dt else 0, path)

    files.sort(key=by_date)

    books, returns, skipped = {}, {}, []
    for path in files:
        with open(path, "rb") as f:
            msg = email.message_from_binary_file(f)
        subj = decode_subject(msg)
        kind = classify(subj)
        body = decode_body(msg)
        if kind == "return":
            d = extract_fields(body, MAIL_RETURN_FIELDS)
            no = (d.get("予約番号") or "").strip()
            if not no:
                skipped.append(os.path.basename(path))
                continue
            d["_file"] = os.path.basename(path)
            d["_subject"] = subj
            returns[no] = d
        elif kind == "book":
            d = extract_fields(body, MAIL_BOOK_FIELDS)
            no = (d.get("予約番号") or "").strip()
            if not no:
                skipped.append(os.path.basename(path))
                continue
            d["_file"] = os.path.basename(path)
            d["_subject"] = subj
            books[no] = d
        else:
            skipped.append(os.path.basename(path))

    if skipped:
        print(f"  跳过（非预约/返却証邮件，共 {len(skipped)} 封）")
    return books, returns


# ---------------- CSV 侧 ----------------

def load_site_from_dir():
    """从 `site/*.csv` 读取「利用料金」明细行。仅供 ingest.py 使用。"""
    rows = []
    for path in sorted(glob.glob(os.path.join(SITE_DIR, "*.csv"))):
        with open(path, "r", encoding="cp932", errors="replace", newline="") as f:
            for r in csv.DictReader(f):
                if not any((v or "").strip() for v in r.values()):
                    continue
                if (r.get("項目名") or "").strip() != CSV_MAIN_ITEM:
                    continue
                if not (r.get("予約開始日時") or "").strip():
                    continue
                r["_file"] = os.path.basename(path)
                rows.append(r)
    return rows


def load_mails():
    """从快照 `data/snapshot.md` 读取（正式数据源）。

    原始 .eml 由 ingest.py 并入快照后即可删除，本函数不再读目录。
    """
    from snapshot import load_snapshot

    books, returns, _ = load_snapshot()
    return books, returns


def load_site():
    """从快照读取官网 CSV 明细行。"""
    from snapshot import load_snapshot

    _, _, rows = load_snapshot()
    return rows


# ---------------- 合并 ----------------

def build_record(no, ret, book, site_row, extras):
    """把 返却証 / CSV実績 / 预约邮件 合成一条记录。"""
    extra = {}
    if ret:
        station = ret.get("ステーション", "")
        car = ret.get("車両", "")
        a_start, a_end = parse_range(ret.get("利用時間", ""))
        minutes = diff_minutes(a_start, a_end)
        km = to_int(ret.get("走行距離", ""))
        yen = to_int(ret.get("合計金額", ""))
        b_start, _ = parse_range(ret.get("予約時間", ""))
        booked = b_start
        extra = {k: ret.get(k, "") for k in ("最高速度", "急加速回数", "急減速回数")}
        src = "返却証"
    elif site_row:
        station = site_row.get("ステーション", "")
        car = ""
        a_start = norm_datetime(site_row.get("利用開始日時", ""))
        a_end = norm_datetime(site_row.get("利用終了日時", ""))
        minutes = to_int(site_row.get("利用時間", ""))
        km = to_int(site_row.get("走行距離", ""))
        yen = to_int(site_row.get("請求金額", ""))
        booked = ""
        src = "CSV"
    else:
        return None, {}

    if book:
        car = car or book.get("車両", "")
        station = station or book.get("ステーション", "")
        booked = booked or norm_datetime(book.get("利用開始日時", ""))

    if extra:
        extras[no] = extra

    sort_key = norm_datetime(a_start) or booked
    return {
        "予約番号": no,
        "予約開始日時": fmt_slash(booked),
        "利用開始": a_start,
        "利用終了": a_end,
        "ステーション": station,
        "車両": car,
        "利用時間": minutes,
        "走行距離": km,
        "請求金額": yen,
        "_sort": sort_key,
        "_src": src,
    }, extra


def main():
    books, returns = load_mails()
    site_rows = load_site()
    print(f"预约邮件（予約登録/変更完了）：{len(books)} 条")
    print(f"返却証邮件（含実績）：        {len(returns)} 条")
    print(f"CSV 利用明细：                {len(site_rows)} 条")

    # CSV 索引: (预约开始时刻, 站点) -> 明细行
    site_index = {}
    for r in site_rows:
        key = (norm_datetime(r.get("予約開始日時", "")), norm_station(r.get("ステーション", "")))
        site_index.setdefault(key, r)

    merged, extras = [], {}
    used_site_keys = set()
    covered = set()

    # 1) 有返却証的：実績以返却証为准
    for no, ret in returns.items():
        rec, _ = build_record(no, ret, books.get(no), None, extras)
        if rec:
            merged.append(rec)
            covered.add(no)

    # 2) 没返却証的：退回用 CSV 実績兜底
    for no, b in books.items():
        if no in covered:
            continue
        key = (norm_datetime(b.get("利用開始日時", "")), norm_station(b.get("ステーション", "")))
        s = site_index.get(key)
        if not s:
            continue
        used_site_keys.add(key)
        rec, _ = build_record(no, None, b, s, extras)
        if rec:
            merged.append(rec)
            covered.add(no)

    unmatched_mail = [(no, b) for no, b in books.items() if no not in covered]
    unmatched_site = [r for k, r in site_index.items() if k not in used_site_keys]

    merged.sort(key=lambda x: (x["_sort"], x["予約番号"]))

    n_ret = sum(1 for x in merged if x["_src"] == "返却証")
    n_csv = len(merged) - n_ret
    total = sum(x["請求金額"] for x in merged)
    total_km = sum(x["走行距離"] for x in merged)
    total_min = sum(x["利用時間"] for x in merged)

    lines = [
        "# 租车记录一览（邮件返却証 × 预约邮件 × 网站明细 整合）",
        "",
        f"- 数据来源优先级：`mail/*.eml` 的**返却証**（実績）> `site/*.csv`（実績兜底）> `mail/*.eml` 的**予約登録/変更完了**（预约信息）",
        f"- 关联键：返却証与预约邮件均含 `予約番号`，直接按键关联；CSV 无该列，用「预约开始时间 + ステーション」关联",
        f"- 收录 {len(merged)} 条（返却証 {n_ret} 条 / CSV 兜底 {n_csv} 条）",
        f"- `利用時間` 单位为**分钟**；`走行距離` 单位 km；`請求金額` 单位 円（返却証取「合計金額」）",
        f"- 合计：利用時間 {total_min:,} 分（{minutes_to_hm(total_min)}）｜走行距離 {total_km:,} km｜請求金額 {total:,} 円",
        "",
        "| 予約番号 | 予約開始日時 | 利用開始（実績） | 利用終了（実績） | ステーション | 車両 | 利用時間(分) | 走行距離(km) | 請求金額(円) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for x in merged:
        lines.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            x["予約番号"], x["予約開始日時"], x["利用開始"], x["利用終了"],
            x["ステーション"], x["車両"], x["利用時間"], x["走行距離"], x["請求金額"]))

    if extras:
        lines += ["", "## 驾驶行为（来自返却証，网页暂未展示）", "",
                  "| 予約番号 | 最高速度 | 急加速回数 | 急減速回数 |", "| --- | --- | --- | --- |"]
        for no in sorted(extras):
            e = extras[no]
            lines.append("| {} | {} | {} | {} |".format(
                no, e.get("最高速度", ""), e.get("急加速回数", ""), e.get("急減速回数", "")))

    if unmatched_mail:
        lines += ["", f"## 仅预约邮件存在（无返却証且无 CSV 実績，未收录）：{len(unmatched_mail)} 条", "",
                  "| 予約番号 | 利用開始日時 | ステーション | 車両 |", "| --- | --- | --- | --- |"]
        for no, m in sorted(unmatched_mail, key=lambda t: norm_datetime(t[1].get("利用開始日時", ""))):
            lines.append("| {} | {} | {} | {} |".format(
                no, m.get("利用開始日時", ""), m.get("ステーション", ""), m.get("車両", "")))

    if unmatched_site:
        lines += ["", f"## 仅 CSV 存在（无对应预约邮件，未收录）：{len(unmatched_site)} 条", "",
                  "| 予約開始日時 | ステーション | 請求金額 |", "| --- | --- | --- |"]
        for r in sorted(unmatched_site, key=lambda r: norm_datetime(r.get("予約開始日時", ""))):
            lines.append("| {} | {} | {} |".format(
                r.get("予約開始日時", ""), r.get("ステーション", ""), r.get("請求金額", "")))

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\n已生成 {OUT_FILE}")
    print(f"  收录 {len(merged)} 条（返却証 {n_ret} / CSV {n_csv}）"
          f" / 仅预约 {len(unmatched_mail)} 条 / 仅 CSV {len(unmatched_site)} 条")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
