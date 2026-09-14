#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""探查 site/*.csv 结构（cp932 编码）。"""
import csv
import glob
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(BASE, "site")

sys.stdout.reconfigure(encoding="utf-8")

files = sorted(glob.glob(os.path.join(SITE_DIR, "*.csv")))
print("文件数:", len(files))

all_rows = []
for p in files:
    with open(p, "r", encoding="cp932", errors="replace", newline="") as f:
        rdr = csv.DictReader(f)
        rows = [r for r in rdr if any((v or "").strip() for v in r.values())]
    print(f"\n=== {os.path.basename(p)} : {len(rows)} 行 ===")
    print("列名:", rdr.fieldnames)
    for r in rows:
        all_rows.append(r)
        print(" | ".join([
            r.get("項目名", ""),
            r.get("予約開始日時", ""),
            r.get("利用開始日時", ""),
            r.get("利用終了日時", ""),
            r.get("ステーション", ""),
            r.get("利用時間", ""),
            r.get("走行距離", ""),
            r.get("請求金額", ""),
        ]))

print("\n总行数:", len(all_rows))
from collections import Counter
print("項目名分布:", Counter(r.get("項目名", "") for r in all_rows))
