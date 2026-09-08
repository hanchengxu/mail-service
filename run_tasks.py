"""按 YAML 配置批量执行收信任务。

用法：
    python run_tasks.py                 # 默认读取同目录 tasks.yml
    python run_tasks.py my_tasks.yml    # 指定配置文件
    python run_tasks.py --stop-on-error # 遇到失败立即停止

配置格式见 tasks.yml：一个数组，每个元素是一个动作。
任意任务加 ignore: true 即可跳过（临时停用，不用删除该条）。
任意任务加 actions: [脚本路径] 可把该任务的输出文本通过 stdin 交给脚本二次处理。
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # 服务器上常见：只拷了代码没装依赖
    sys.exit(
        "缺少依赖 PyYAML。请先安装：\n"
        "  pip install -r requirements.txt\n"
        "  或 pip install pyyaml   /   apt install python3-yaml"
    )

from config import load_settings
from imap_qq_test import SCOPE_NAMES, print_folders
from logger import log, log_path
from mail_client import QQMailClient

DEFAULT_CONFIG = Path(__file__).with_name("tasks.yml")
STATE_DIR = Path(__file__).with_name("state")


# ---------------- once_per_day：每天只成功执行一次 ----------------
def _state_file() -> Path:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    return STATE_DIR / "once_per_day.json"


def _load_state() -> dict:
    path = _state_file()
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def already_run_today(key: str) -> bool:
    return _load_state().get(key) == datetime.now().strftime("%Y-%m-%d")


def mark_run_today(key: str) -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    state = {k: v for k, v in _load_state().items() if v == today}
    state[key] = today
    try:
        _state_file().write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError as exc:
        log(f"写入 once_per_day 状态失败：{exc}", "WARN")


class NoMailFound(Exception):
    """任务没读到任何邮件（不是错误，只是没有可处理的内容）。"""


def _header(index: int, total: int, name: str) -> None:
    print("\n" + "=" * 72)
    print(f"[{index}/{total}] {name}")
    print("=" * 72)


def run_read(client: QQMailClient, cfg: dict) -> None:
    msg = client.read_message(
        folder_name=cfg["folder"],
        title_contains=cfg.get("title_contains"),
        nth=int(cfg.get("nth", 1)),
        read_status=cfg.get("read_status", "unread"),
        order=cfg.get("order", "newest"),
    )
    if msg is None:
        extra = f"、标题包含 '{cfg.get('title_contains')}'" if cfg.get("title_contains") else ""
        print(
            f"没有找到第 {cfg.get('nth', 1)} 封邮件"
            f"（文件夹 [{cfg['folder']}]{extra}，范围：{SCOPE_NAMES[cfg.get('read_status', 'unread')]}）"
        )
        raise NoMailFound("没有匹配的邮件")

    print(f"UID     : {msg.uid}")
    print(f"主题    : {msg.subject}")
    print(f"发件人  : {msg.sender}")
    print(f"时间    : {msg.date}")

    body = msg.body or "(无正文)"
    limit = cfg.get("max_body_chars")
    if limit and len(body) > limit:
        body = body[: int(limit)] + f"\n...（已截断，共 {len(body)} 字）"
    print("-" * 72)
    print(body)


def run_list_matches(client: QQMailClient, cfg: dict) -> None:
    matches = client.search(
        folder_name=cfg["folder"],
        read_status=cfg.get("read_status", "unread"),
        title_contains=cfg.get("title_contains"),
        order=cfg.get("order", "newest"),
        limit=cfg.get("limit", 20),
    )
    print(
        f"命中 {len(matches)} 封"
        f"（范围：{SCOPE_NAMES[cfg.get('read_status', 'unread')]}，排序：{cfg.get('order', 'newest')}）"
    )
    for i, m in enumerate(matches, 1):
        print(f"  {i:>3}. [{m.date}] {m.subject}")
        print(f"        from: {m.sender}")


def run_list_folders(client: QQMailClient, cfg: dict) -> None:
    print_folders(client)


ACTIONS = {
    "read": (run_read, {"folder"}),
    "list_matches": (run_list_matches, {"folder"}),
    "list_folders": (run_list_folders, set()),
}


def resolve_script(script: str, base_dir: Path) -> Path:
    """action 脚本路径：绝对路径直接用，相对路径优先相对配置文件所在目录。"""
    path = Path(script)
    if path.is_absolute() or path.is_file():
        return path
    return base_dir / path


def run_post_actions(output: str, scripts, base_dir: Path) -> int:
    """把任务输出通过 stdin 交给 action 脚本；多个脚本串联，上一个的输出作为下一个的输入。

    返回失败数。
    """
    failed = 0
    text = output
    for script in scripts:
        path = resolve_script(str(script), base_dir)
        if not path.is_file():
            msg = f"找不到 action 脚本：{path}"
            print(f"\n[失败] {msg}，链路中断")
            log(msg, "ERROR")
            failed += 1
            break

        print(f"\n---- 执行 action：{path.as_posix()} ----")
        log(f"执行 action：{path.as_posix()}")
        try:
            result = subprocess.run(
                [sys.executable, str(path)],
                input=text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
        except Exception as exc:
            msg = f"action {path.name} 无法执行：{type(exc).__name__}: {exc}"
            print(f"[失败] {msg}")
            log(f"{msg}\n{traceback.format_exc()}", "ERROR")
            failed += 1
            break

        if result.stdout:
            print(result.stdout.rstrip())
        if result.returncode != 0:
            detail = result.stderr.strip() if result.stderr else f"退出码 {result.returncode}"
            msg = f"action {path.name} 失败：{detail}"
            print(f"[失败] {msg}")
            log(msg, "ERROR")
            failed += 1
            break  # 失败即中断链路，后面的 action（如朗读）不再执行

        if not result.stdout.strip():
            msg = f"action {path.name} 没有输出，链路中断"
            print(f"[中断] {msg}")
            log(msg, "WARN")
            break

        text = result.stdout  # 串联：交给下一个 action
    return failed


def run_action(client: QQMailClient, cfg: dict, index: int, total: int) -> None:
    if not isinstance(cfg, dict) or "action" not in cfg:
        raise ValueError(f"第 {index} 个任务缺少 action 字段：{cfg!r}")

    action = cfg["action"]
    if action not in ACTIONS:
        raise ValueError(f"未知动作 '{action}'，可用：{list(ACTIONS)}")

    handler, required = ACTIONS[action]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise ValueError(f"动作 '{action}' 缺少必填字段：{missing}")

    name = cfg.get("name") or action
    _header(index, total, f"{name}  [{action}]")
    handler(client, cfg)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="按 YAML 配置批量执行收信任务")
    parser.add_argument("config", nargs="?", default=str(DEFAULT_CONFIG), help="YAML 配置文件路径")
    parser.add_argument("--stop-on-error", action="store_true", help="遇到失败立即停止")
    parser.add_argument(
        "--force", action="store_true", help="忽略 once_per_day，强制执行一次"
    )
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    if not config_path.is_file():
        sys.exit(f"配置文件不存在：{config_path}")

    tasks = yaml.safe_load(config_path.read_text(encoding="utf-8")) or []
    if not isinstance(tasks, list):
        sys.exit("配置文件内容必须是一个数组（以 - 开头的任务列表）")

    print(f"加载配置 {config_path}，共 {len(tasks)} 个任务")
    log("=" * 60)
    log(f"开始执行配置 {config_path}，共 {len(tasks)} 个任务")
    settings = load_settings()

    failed = 0
    skipped = 0
    with QQMailClient(settings) as client:
        print(f"已连接 {settings.host}:{settings.port}，账号 {settings.username}")
        log(f"已连接 {settings.host}:{settings.port}，账号 {settings.username}")
        for i, cfg in enumerate(tasks, 1):
            if isinstance(cfg, dict) and cfg.get("ignore"):
                skipped += 1
                name = cfg.get("name") or cfg.get("action") or "未命名任务"
                print(f"[跳过] {i}/{len(tasks)} {name}（ignore: true）")
                log(f"跳过任务 {i}/{len(tasks)}：{name}（ignore: true）", "WARN")
                continue

            opts = cfg if isinstance(cfg, dict) else {}
            task_key = str(opts.get("name") or opts.get("action") or i)

            # once_per_day：今天已经成功跑过就跳过，避免高频定时重复播报
            if opts.get("once_per_day") and not args.force and already_run_today(task_key):
                skipped += 1
                print(f"[跳过] {i}/{len(tasks)} {task_key}（once_per_day：今天已成功执行过）")
                log(f"跳过任务 {i}/{len(tasks)}：{task_key}（今天已执行）", "WARN")
                continue

            log(f"任务 {i}/{len(tasks)} 开始：{task_key}")
            failed_before = failed
            # 捕获任务输出，便于后续传给 action 脚本
            buf = io.StringIO()
            no_content = False
            try:
                with contextlib.redirect_stdout(buf):
                    run_action(client, cfg, i, len(tasks))
            except NoMailFound as exc:
                log(f"任务 {i}/{len(tasks)} 无内容：{exc}", "WARN")
                no_content = True
            except Exception as exc:
                failed += 1
                buf.write(f"[失败] 第 {i} 个任务：{type(exc).__name__}: {exc}\n")
                log(f"任务 {i}/{len(tasks)} 失败：{exc}\n{traceback.format_exc()}", "ERROR")
            output = buf.getvalue()

            scripts = opts.get("actions")
            if isinstance(scripts, str):
                scripts = [scripts]

            # quiet：不打印任务自身的输出（正文等），只把它传给 action 脚本。
            # 未显式配置时，挂了 actions 的任务默认 quiet。
            quiet = opts.get("quiet")
            if quiet is None:
                quiet = bool(scripts)

            if quiet and not no_content:
                print(f"（任务输出 {len(output)} 字已传给 action，未在控制台打印）")
            else:
                sys.stdout.write(output)

            if scripts and no_content:
                print("[中断] 没有可读内容，跳过该任务的 actions（不朗读）")
            elif scripts:
                failed += run_post_actions(output, scripts, config_path.parent)

            # 只在「有内容且没失败」时记一次，保证邮件晚到时还会继续轮询
            if opts.get("once_per_day") and not no_content and failed == failed_before:
                mark_run_today(task_key)
                log(f"记录 once_per_day 完成：{task_key}")

            if failed and args.stop_on_error:
                break

    summary = (
        f"执行完成：共 {len(tasks)} 个任务，"
        f"执行 {len(tasks) - skipped - failed} 个，跳过 {skipped} 个，失败 {failed} 个"
    )
    print("\n" + "=" * 72)
    print(summary)
    print(f"日志文件：{log_path()}")
    log(summary, "ERROR" if failed else "INFO")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
