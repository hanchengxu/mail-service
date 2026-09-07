"""把 rakuten-sec-action.py 的盈亏结论转成适合朗读的中文（stdin → stdout）。

只做文本转换，不碰 Home Assistant，方便单独调试或换别的播报渠道。

用法：
    # tasks.yml 中串联
    actions:
      - actions/rakuten-sec-action.py   # 今日盈亏（原始结论）
      - actions/rakuten-sec-speech.py   # 转成口语化文本
      - actions/xiaoai-voice-action.py  # 通用朗读

    # 单独使用
    echo "本日損益（各ファンド1万口換算の合計）：-823円（-0.29%）⇒ 亏损" | python actions/rakuten-sec-speech.py
    python actions/rakuten-sec-speech.py result.txt
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MAX_CHARS = 255

# 符号 -> 朗读时的读法/停顿
REPLACEMENTS = {
    "｜": "，",
    "⇒": "，",
    "→": "，",
    "（": "，",
    "）": "，",
    "(": "，",
    ")": "，",
    "：": "，",
    "％": "%",
    "、": "，",
    "円": "日元",
    "\n": "。",
}


def to_speech(text: str) -> str:
    """把统计结论整理成适合朗读的中文。"""
    text = text.strip()
    if not text:
        return ""
    # 正负号读法：-823円 -> 负823日元
    text = re.sub(r"([+-])(\d)", lambda m: ("负" if m.group(1) == "-" else "正") + m.group(2), text)
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    text = re.sub(r"\s*，\s*", "，", text)
    text = re.sub(r"，{2,}", "，", text)
    text = re.sub(r"\s+", " ", text).strip("， ")
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
    return text


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        path = Path(argv[1])
        if not path.is_file():
            print(f"文件不存在：{path}")
            return 1
        text = path.read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()

    speech = to_speech(text)
    if not speech:
        print("[无数据] 输入为空或转换后没有可朗读的内容", file=sys.stderr)
        return 1
    print(speech)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
