"""通用 action：把上游邮件标记为已读（stdin 文本里需含「UID」和「文件夹」两行）。

建议放在链路最后一步：只有前面的解析、朗读都成功后才会执行，
万一朗读失败，邮件保持未读，下次轮询会再试一次。

用法：
    actions:
      - actions/amazon/amazon-send-action.py
      - actions/xiaoai-voice-action.py
      - actions/mark-read-action.py      # 最后标记已读

    # 单独使用
    python actions/mark-read-action.py mail.txt

环境变量：
    MARK_AS=unread   反向操作（标记成未读），用于补救
    HA_DRY_RUN=1     只打印将要执行的操作，不真正改状态

说明：本脚本放在链路最后一步，此时 stdin 已是上一个 action 的输出（不含 UID）。
因此会回退读取环境变量 MAIL_TASK_OUTPUT 指向的文件——run_tasks.py 会把任务原始输出
（含 UID / 文件夹）写到该文件并传给每个 action。
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import load_settings  # noqa: E402
from mail_client import QQMailClient  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

UID_PATTERN = re.compile(r"UID\s*[:：]\s*(\d+)")
FOLDER_PATTERN = re.compile(r"文件夹\s*[:：]\s*(.+)")


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        path = Path(argv[1])
        if not path.is_file():
            print(f"文件不存在：{path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()

    uid_match, folder_match = UID_PATTERN.search(text), FOLDER_PATTERN.search(text)
    if not (uid_match and folder_match):
        # 上游是别的 action 时，回退到任务原始输出（run_tasks.py 提供的临时文件）
        backup = os.environ.get("MAIL_TASK_OUTPUT")
        if backup and Path(backup).is_file():
            text = Path(backup).read_text(encoding="utf-8", errors="replace")
            uid_match, folder_match = UID_PATTERN.search(text), FOLDER_PATTERN.search(text)
    if not uid_match or not folder_match:
        print(
            "[无数据] 输入里没有找到 UID / 文件夹 信息（需要 read 任务的输出）",
            file=sys.stderr,
        )
        return 1

    uid = uid_match.group(1)
    folder = folder_match.group(1).strip()
    seen = os.environ.get("MARK_AS", "read").lower() != "unread"
    dry_run = bool(os.environ.get("HA_DRY_RUN"))

    if dry_run:
        print(f"[dry-run] 将把 {folder} 中 UID={uid} 标记为{'已读' if seen else '未读'}")
        return 0

    with QQMailClient(load_settings()) as client:
        client.set_seen(folder, uid, seen=seen)
    print(f"已标记为{'已读' if seen else '未读'}：UID {uid}（{folder}）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
