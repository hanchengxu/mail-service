#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 `mail/*.eml` 与 `site/*.csv` 并入 `data/snapshot.md`，并删除已并入的原始文件。

并入后就不再需要原始文件了——快照是唯一数据源，后续 parse_mail.py 只读快照。

用法：
    python ingest.py               # 并入并删除已并入的原始文件（默认）
    python ingest.py --keep        # 并入但保留原始文件
    python ingest.py --dry-run     # 只统计，不写快照也不删文件

幂等：同一批数据反复并入结果一致（按 予約番号 / 「予約開始日時+ステーション」 后覆盖前）。
"""

import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import parse_mail as pm  # noqa: E402
from snapshot import SNAPSHOT, load_snapshot, save_snapshot  # noqa: E402


def merge_csv(old_rows, new_rows):
    """按（予約開始日時, ステーション）去重，新的覆盖旧的。"""
    idx = {}
    for r in list(old_rows) + list(new_rows):
        key = (
            pm.norm_datetime(r.get("予約開始日時", "")),
            pm.norm_station(r.get("ステーション", "")),
        )
        idx[key] = r
    return list(idx.values())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="把原始邮件/CSV 并入快照")
    ap.add_argument("--keep", action="store_true", help="并入后保留原始文件")
    ap.add_argument("--dry-run", action="store_true", help="只统计，不写不删")
    args = ap.parse_args(argv)

    new_books, new_returns = pm.load_mails_from_dir()
    new_csv = pm.load_site_from_dir()
    books, returns, csv_rows = load_snapshot()

    print(f"快照现有：预约 {len(books)} 条 / 返却証 {len(returns)} 条 / CSV {len(csv_rows)} 条")
    print(f"本次读入：预约 {len(new_books)} 条 / 返却証 {len(new_returns)} 条 / CSV {len(new_csv)} 条")

    if not (new_books or new_returns or new_csv):
        print("没有新数据，快照保持不变")
        return 0

    books.update(new_books)
    returns.update(new_returns)
    csv_rows = merge_csv(csv_rows, new_csv)
    print(f"合并后  ：预约 {len(books)} 条 / 返却証 {len(returns)} 条 / CSV {len(csv_rows)} 条")

    if args.dry_run:
        print("[dry-run] 未写快照、未删原始文件")
        return 0

    save_snapshot(books, returns, csv_rows)
    print(f"已写入快照：{SNAPSHOT}")

    if args.keep:
        print("[--keep] 保留原始文件")
        return 0

    removed = 0
    for directory, pattern in ((pm.MAIL_DIR, "*.eml"), (pm.SITE_DIR, "*.csv")):
        if not os.path.isdir(directory):
            continue
        for path in sorted(glob.glob(os.path.join(directory, pattern))):
            try:
                os.remove(path)
                removed += 1
            except OSError as exc:
                print(f"  [跳过] 删除失败 {path}: {exc}")
    print(f"已删除原始文件 {removed} 个（mail/*.eml 与 site/*.csv）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
