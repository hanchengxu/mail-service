"""极简日志：按天追加到 logs/app-YYYYMMDD.log。

用法：
    from logger import log
    log("任务开始")                 # 只写文件
    log("连接失败", "ERROR", echo=True)  # 写文件并打印到控制台

level：INFO / WARN / ERROR，仅影响日志里的标记。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).with_name("logs")


def log_path() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR / f"app-{datetime.now():%Y%m%d}.log"


def log(message: str, level: str = "INFO", echo: bool = False) -> None:
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {level:<5} {message}"
    try:
        with log_path().open("a", encoding="utf-8") as fp:
            fp.write(line + "\n")
    except OSError:
        pass  # 日志写失败不影响主流程
    if echo:
        print(message)
