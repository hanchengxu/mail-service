"""配置加载：真实环境变量优先，其次读取同目录 .env（零第三方依赖）。"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

ENV_FILE = Path(__file__).with_name(".env")


def load_env_file(path: Path = ENV_FILE) -> None:
    """极简 .env 加载器：支持 # 注释、export 前缀、单/双引号，不覆盖已有环境变量。"""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.lower().startswith("export "):
            line = line[len("export ") :]
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


def env(key: str, default=None, required: bool = False):
    value = os.environ.get(key, default)
    if required and (value is None or value == ""):
        sys.exit(f"缺少配置项 {key}。请执行：copy .env.example .env 并填写真实值。")
    return value


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    timeout: int
    username: str
    auth_code: str


def load_settings() -> Settings:
    try:  # 装了 python-dotenv 就用它，否则用内置加载器
        from dotenv import load_dotenv

        load_dotenv(ENV_FILE, override=False)
    except ImportError:
        load_env_file()

    return Settings(
        host=env("QQ_MAIL_HOST", "imap.qq.com"),
        port=int(env("QQ_MAIL_PORT", 993)),
        timeout=int(env("QQ_MAIL_TIMEOUT", 30)),
        username=env("QQ_MAIL_USER", required=True),
        auth_code=env("QQ_MAIL_AUTH", required=True),
    )
