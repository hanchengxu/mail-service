"""Amazon「配達中」邮件 -> 一句固定播报文本（stdin → stdout）。

不解析邮件正文，只要文本里出现「配達中」就输出固定文案，日期取邮件时间（换算成日本时间）。

用法：
    # tasks.yml 中串联
    actions:
        - actions/amazon/amazon-send-action.py   # 生成播报文案
        - actions/xiaoai-voice-action.py         # 通用朗读

    # 单独使用
    echo "时间    : Sun, 06 Sep 2026 23:31:35 +0000" | python actions/amazon/amazon-send-action.py
    python actions/amazon/amazon-send-action.py mail.txt
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KEYWORD = "配達中"
JST = timezone(timedelta(hours=9))

# 匹配任务输出里的时间行，或邮件原始 Date 头
DATE_PATTERNS = [
    re.compile(r"时间\s*[:：]\s*(.+)"),
    re.compile(r"Date\s*[:：]\s*(.+)"),
    re.compile(r"\w{3},\s*\d{1,2}\s+\w{3}\s+\d{4}\s+[\d:]+\s*[+-]\d{4}"),
]


def mail_date(text: str) -> datetime | None:
    """从文本里找邮件时间，找不到返回 None。"""
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        raw = (match.group(1) if pattern.groups else match.group(0)).strip()
        try:
            return parsedate_to_datetime(raw)
        except Exception:
            continue
    return None


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        path = Path(argv[1])
        if not path.is_file():
            print(f"文件不存在：{path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()

    if KEYWORD not in text:
        print(f"[无数据] 文本中没有「{KEYWORD}」，不是配送通知", file=sys.stderr)
        return 1

    sent = mail_date(text)
    when = sent.astimezone(JST) if sent else datetime.now(JST)
    print(f"您好，{when.month}月{when.day}日，有亚马逊快递正在配送")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
