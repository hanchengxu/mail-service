"""QQ 邮箱 IMAP 命令行工具。

用法示例：
    python imap_qq_test.py --list-folders                       # 列出所有文件夹
    python imap_qq_test.py INBOX                                # 读最新 1 封未读的正文
    python imap_qq_test.py "其他文件夹/楽天証券" --title "請求" --nth 1
    python imap_qq_test.py INBOX --title "验证码" --list-matches # 只列匹配的邮件摘要
    python imap_qq_test.py INBOX --all --nth 3 --order oldest   # 全部邮件里第 3 封（从旧到新）

代码里直接调用：
    from config import load_settings
    from mail_client import QQMailClient

    with QQMailClient(load_settings()) as client:
        msg = client.read_message("INBOX", title_contains="账单", nth=1)
        print(msg.body)
"""

from __future__ import annotations

import argparse
import sys
import unicodedata

from config import load_settings
from mail_client import QQMailClient, MailMessage

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _pad(text: str, width: int) -> str:
    """按终端显示宽度（中日韩全角字符占 2 列）左对齐补齐。"""
    wide = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)
    return text + " " * max(0, width - wide)


def print_folders(client: QQMailClient) -> None:
    folders = client.list_folders()
    print(f"\n共发现 {len(folders)} 个文件夹：\n")
    print(f"{'#':>3}  {_pad('文件夹', 32)}{'总数':>7}{'未读':>7}   属性")
    print("-" * 90)
    for i, folder in enumerate(folders, 1):
        total, unseen = ("-", "-")
        if folder.selectable:
            t, u = client.message_count(folder.name)
            total, unseen = (t or "-"), (u or "-")
        print(f"{i:>3}  {_pad(folder.name, 32)}{total:>7}{unseen:>7}   {folder.flags}")


SCOPE_NAMES = {"unread": "未读", "read": "已读", "all": "全部"}


def print_matches(client: QQMailClient, args) -> int:
    matches = client.search(
        args.folder,
        read_status=args.status,
        title_contains=args.title,
        order=args.order,
        limit=args.limit,
    )
    print(
        f"\n文件夹 [{args.folder}] 命中 {len(matches)} 封"
        f"（范围：{SCOPE_NAMES[args.status]}，排序：{args.order}）\n"
    )
    for i, m in enumerate(matches, 1):
        print(f"{i:>3}. [{m.date}] {m.subject}")
        print(f"      from: {m.sender}")
    return 0


def print_message(msg: MailMessage | None, args) -> int:
    if msg is None:
        extra = f"、标题包含 '{args.title}'" if args.title else ""
        print(
            f"没有找到第 {args.nth} 封邮件"
            f"（文件夹 [{args.folder}]{extra}，范围：{SCOPE_NAMES[args.status]}）"
        )
        return 1

    print("=" * 70)
    print(f"UID     : {msg.uid}")
    print(f"主题    : {msg.subject}")
    print(f"发件人  : {msg.sender}")
    print(f"收件人  : {msg.to}")
    print(f"时间    : {msg.date}")
    print("=" * 70)
    print(msg.body or "(无正文)")
    print("=" * 70)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QQ 邮箱 IMAP 收信工具（配置读取同目录 .env）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("folder", nargs="?", help="文件夹名，如 INBOX 或 其他文件夹/楽天証券")
    parser.add_argument("-t", "--title", help="标题需包含的字符串（忽略大小写）")
    parser.add_argument(
        "-n", "--nth", type=int, default=1, help="第几封，从 1 开始，默认 1（最新一封）"
    )
    parser.add_argument(
        "--status",
        choices=["unread", "read", "all"],
        default="unread",
        help="读取范围：未读/已读/全部，默认 unread",
    )
    parser.add_argument("--all", action="store_true", help="等价于 --status all")
    parser.add_argument(
        "--order", choices=["newest", "oldest"], default="newest", help="排序，默认 newest"
    )
    parser.add_argument("--list-folders", action="store_true", help="列出所有文件夹后退出")
    parser.add_argument("--list-matches", action="store_true", help="只列出命中的邮件摘要")
    parser.add_argument("--limit", type=int, default=20, help="--list-matches 最多显示条数，默认 20")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.all:  # 兼容旧写法：--all = --status all
        args.status = "all"
    settings = load_settings()

    with QQMailClient(settings) as client:
        print(f"已连接 {settings.host}:{settings.port}，账号 {settings.username}")

        if args.list_folders or not args.folder:
            print_folders(client)
            if not args.folder:
                print("\n提示：加文件夹名可读取邮件，例如：python imap_qq_test.py INBOX")
            return 0

        if args.list_matches:
            return print_matches(client, args)

        msg = client.read_message(
            args.folder,
            title_contains=args.title,
            nth=args.nth,
            read_status=args.status,
            order=args.order,
        )
        return print_message(msg, args)


if __name__ == "__main__":
    sys.exit(main())
