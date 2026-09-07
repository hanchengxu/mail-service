"""通用播报 action：把 stdin 里的文本交给 Home Assistant，让小爱音箱朗读。

本脚本不做任何业务相关的文本改写（那是各自预处理脚本的事），只负责：
    读入文本 -> 通用清洗（去多余空白、按长度截断）-> 调用 HA -> 打印结果

需要针对某种邮件做口语化时，在它前面串一个预处理脚本，例如：
    actions:
      - actions/rakuten-sec-action.py   # 产出「今日盈亏」结论
      - actions/rakuten-sec-speech.py   # 转成口语化文本（业务相关）
      - actions/xiaoai-voice-action.py  # 通用朗读

单独使用：
    echo "今天天气不错" | python actions/xiaoai-voice-action.py
    python actions/xiaoai-voice-action.py message.txt

.env 配置：
    HA_URL                 Home Assistant 地址，如 http://192.168.1.117:8123
    HA_TOKEN               长期访问令牌（HA 个人资料页最下方创建）
    HA_XIAOAI_ENTITY_ID    小爱音箱实体，如 text.xiaomi_l05b_13c7_play_text（播放文本）
                           若填 media_player.xxx，则改用 tts.speak 播报
    HA_TTS_ENTITY          用 media_player 方式时的 tts 实体，如 tts.xiaomi_tts
    HA_MAX_CHARS           朗读文本最大长度，默认 255
    HA_DRY_RUN=1           只打印将要发送的内容，不真正调用 HA（调试用）
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import env, load_env_file  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

load_env_file()


def prepare_text(text: str) -> str:
    """通用清洗：只处理空白与长度，不改写业务内容。"""
    text = text.strip()
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    max_chars = int(env("HA_MAX_CHARS", 255))
    if len(text) > max_chars:
        text = text[:max_chars]
    return text


def build_request(message: str):
    """返回 (service 路径, payload)。"""
    entity = env("HA_XIAOAI_ENTITY_ID", required=True)
    if entity.startswith("media_player."):
        return "tts/speak", {
            "entity_id": env("HA_TTS_ENTITY", ""),
            "media_player_entity_id": entity,
            "message": message,
        }
    return env("HA_SERVICE", "text/set_value"), {"entity_id": entity, "value": message}


def call_ha(service: str, payload: dict) -> None:
    base = env("HA_URL", required=True).rstrip("/")
    token = env("HA_TOKEN", required=True)
    url = f"{base}/api/services/{service}"

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"HA 返回 {exc.code}：{detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"无法连接 HA（{url}）：{exc.reason}") from exc


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        path = Path(argv[1])
        if not path.is_file():
            print(f"文件不存在：{path}")
            return 1
        raw = path.read_text(encoding="utf-8", errors="replace")
    else:
        raw = sys.stdin.read()

    message = prepare_text(raw)
    if not message:
        print("输入为空，没有可朗读的内容。")
        return 1

    service, payload = build_request(message)
    if os.environ.get("HA_DRY_RUN"):
        print(
            f"[dry-run] POST {service}\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
            f"\n将朗读：{message}"
        )
        return 0

    try:
        call_ha(service, payload)
    except Exception as exc:
        print(f"朗读失败：{exc}")
        return 1

    print(f"小爱音箱已朗读（{service}）：{message}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
