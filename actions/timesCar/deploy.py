#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把生成的看板（web/ 整个目录）部署到 nginx 站点目录。

web/index.html 用相对路径引用 car/*.png 与 logos/*，所以必须整个目录一起拷，
不能只拷 index.html。

用法：
    python deploy.py                                    # 用默认目标目录
    python deploy.py --dest /usr/local/nginx/html/timescar
    python deploy.py --clean                            # 先清空目标目录再拷（保证完全同步）
    python deploy.py --strict                           # 目标不存在时报错（默认只警告并跳过）

目标目录取值优先级：--dest 参数 > 环境变量 TIMESCAR_DEPLOY_DIR > 脚本内 DEFAULT_DEST。

在 tasks.yml 里作为最后一个 action 使用：
    - actions/timesCar/deploy.py --dest /usr/local/nginx/html/timescar
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "web"

# 服务器上的 nginx 站点目录（不想每次敲 --dest 就改这里）
DEFAULT_DEST = "/usr/local/nginx/html/timescar"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def count_files(root: Path) -> tuple[int, int]:
    """返回 (文件数, 总字节数)。"""
    n = size = 0
    for p in root.rglob("*"):
        if p.is_file():
            n += 1
            try:
                size += p.stat().st_size
            except OSError:
                pass
    return n, size


def ensure_readable(root: Path) -> None:
    """确保 nginx（www-data/nginx 用户）能读：文件 644、目录 755。"""
    try:
        for p in root.rglob("*"):
            if p.is_dir():
                p.chmod(0o755)
            elif p.is_file():
                p.chmod(0o644)
        root.chmod(0o755)
    except OSError as exc:
        print(f"  [警告] 调整权限失败（不影响部署，但 nginx 可能读不到）：{exc}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="部署 timesCar 看板到 nginx 目录")
    ap.add_argument("--dest", default=os.environ.get("TIMESCAR_DEPLOY_DIR") or DEFAULT_DEST,
                    help=f"目标目录，默认 {DEFAULT_DEST}")
    ap.add_argument("--clean", action="store_true", help="部署前先清空目标目录")
    ap.add_argument("--strict", action="store_true",
                    help="目标目录的父目录不存在时报错退出（默认只警告并跳过，方便在非服务器环境调试）")
    args = ap.parse_args(argv)

    if not SRC.is_dir():
        print(f"源目录不存在：{SRC}", file=sys.stderr)
        return 1

    dest = Path(args.dest).expanduser()
    parent = dest.parent

    # 非服务器环境（比如本地开发机没有 nginx 目录）：默认跳过而不是报错
    if not parent.is_dir():
        msg = f"目标目录的父目录不存在：{parent}"
        if args.strict:
            print(msg, file=sys.stderr)
            return 1
        print(f"[跳过] {msg}")
        print("       （本机不是服务器环境，未部署。加 --strict 可改为报错）")
        return 0

    try:
        if args.clean and dest.exists():
            shutil.rmtree(dest)
            print(f"已清空目标目录：{dest}")

        # dirs_exist_ok=True：已存在就合并并覆盖同名文件
        shutil.copytree(SRC, dest, dirs_exist_ok=True)
    except OSError as exc:
        print(f"部署失败：{exc}", file=sys.stderr)
        return 1

    ensure_readable(dest)
    n, size = count_files(dest)
    print(f"已部署 -> {dest}")
    print(f"  共 {n} 个文件，{size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
