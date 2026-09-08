"""QQ 邮箱 IMAP 客户端：连接、列目录、按条件读取邮件正文。"""

from __future__ import annotations

import imaplib
import re
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Iterable, Iterator

from config import Settings
from email_parser import MailMessage, parse_headers, parse_message
from imap_utf7 import imap_utf7_decode, imap_utf7_encode

HEADER_FIELDS = "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])"
CHUNK_SIZE = 50

# 读取范围 -> IMAP SEARCH 条件
READ_STATUS = {"unread": "UNSEEN", "read": "SEEN", "all": "ALL"}


@dataclass
class Folder:
    raw: str  # 服务器上的原始名（modified UTF-7）
    name: str  # 解码后的可读名
    flags: str = ""
    delimiter: str = "/"

    @property
    def selectable(self) -> bool:
        return r"\NoSelect" not in self.flags


@dataclass
class MailSummary:
    uid: str
    subject: str
    sender: str
    date: str


class QQMailClient:
    """IMAP 客户端封装，支持 with 语法：

    with QQMailClient(load_settings()) as client:
        msg = client.read_message("INBOX", title_contains="账单", nth=1)
        print(msg.body)
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.mail: imaplib.IMAP4_SSL | None = None
        self._folders: list[Folder] | None = None

    # ---------------- 生命周期 ----------------
    def connect(self) -> "QQMailClient":
        self.mail = imaplib.IMAP4_SSL(
            self.settings.host, self.settings.port, timeout=self.settings.timeout
        )
        self.mail.login(self.settings.username, self.settings.auth_code)
        return self

    def close(self) -> None:
        if self.mail is None:
            return
        for method in ("close", "logout"):
            try:
                getattr(self.mail, method)()
            except Exception:
                pass
        self.mail = None

    def __enter__(self) -> "QQMailClient":
        return self.connect()

    def __exit__(self, *exc_info) -> None:
        self.close()

    @property
    def conn(self) -> imaplib.IMAP4_SSL:
        if self.mail is None:
            raise RuntimeError("尚未连接，请先调用 connect() 或使用 with 语法")
        return self.mail

    # ---------------- 文件夹 ----------------
    def list_folders(self, refresh: bool = False) -> list[Folder]:
        """列出所有文件夹（结果会缓存，传 refresh=True 强制重新拉取）。"""
        if self._folders is not None and not refresh:
            return self._folders

        typ, data = self.conn.list('""', "*")
        if typ != "OK":
            raise RuntimeError(f"LIST 失败：{typ} {data}")

        folders: list[Folder] = []
        for item in data or []:
            if not item:
                continue
            flags, delimiter, raw = _parse_list_line(item)
            folders.append(
                Folder(
                    raw=raw,
                    name=imap_utf7_decode(raw),
                    flags=flags,
                    delimiter=delimiter,
                )
            )
        self._folders = folders
        return folders

    def resolve_folder(self, name: str) -> Folder:
        """按可读名定位文件夹。

        支持：INBOX / 完整路径（其他文件夹/楽天証券）/ 末级名（楽天証券）/ 中文别名（收件箱）。
        """
        target = _ALIASES.get(name.strip().lower(), name.strip())
        target_encoded = imap_utf7_encode(target)

        folders = self.list_folders()
        for folder in folders:
            if folder.raw == target_encoded or folder.name.lower() == target.lower():
                return folder

        # 退而求其次：唯一包含匹配（可用末级目录名）
        hits = [f for f in folders if target.lower() in f.name.lower()]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            raise ValueError(
                f"文件夹名 '{name}' 匹配到多个：{[f.name for f in hits]}，请写完整路径"
            )
        raise ValueError(f"找不到文件夹：{name}")

    def _select(self, folder: Folder, readonly: bool = True) -> int:
        """打开文件夹。默认只读（EXAMINE，不会置 \\Seen）；写操作需 readonly=False。"""
        if not folder.selectable:
            raise ValueError(f"文件夹 '{folder.name}' 不可选择（\\NoSelect）")
        typ, data = self.conn.select(f'"{folder.raw}"', readonly=readonly)
        if typ != "OK":
            raise RuntimeError(f"打开文件夹 '{folder.name}' 失败：{typ} {data}")
        return int(data[0]) if data and data[0] else 0

    def set_seen(self, folder_name: str, uid: str, seen: bool = True) -> bool:
        """设置邮件已读/未读（唯一会修改邮箱状态的操作）。"""
        folder = self.resolve_folder(folder_name)
        self._select(folder, readonly=False)
        action = "+FLAGS" if seen else "-FLAGS"
        typ, data = self.conn.uid("STORE", uid, action, "(\\Seen)")
        if typ != "OK":
            raise RuntimeError(f"设置 UID={uid} 已读状态失败：{typ} {data}")
        return True

    # ---------------- 检索 / 读取 ----------------
    def search(
        self,
        folder_name: str,
        read_status: str = "unread",
        title_contains: str | None = None,
        order: str = "newest",
        limit: int | None = None,
    ) -> list[MailSummary]:
        """列出符合条件的邮件摘要（只拉头部，较快）。

        :param folder_name:  文件夹名，如 "INBOX"、"其他文件夹/楽天証券"
        :param read_status:  "unread" 未读 / "read" 已读 / "all" 全部
        :param title_contains: 标题需包含的字符串（忽略大小写），None 表示不过滤
        :param order:        "newest" 按发送时间最新在前（默认）/"oldest" 最早在前
        :param limit:        最多返回多少条，None 表示全部

        注意：排序依据是邮件 Date 头，不是 UID——移动过文件夹的邮件 UID 会保留原值，
        与到达时间并不一致。
        """
        folder = self.resolve_folder(folder_name)
        self._select(folder)

        uids = self._search_uids(read_status)
        keyword = title_contains.lower() if title_contains else None

        results: list[MailSummary] = []
        for chunk in _chunks(uids, CHUNK_SIZE):
            for uid, headers in self._fetch_headers(chunk):
                if keyword and keyword not in headers["subject"].lower():
                    continue
                results.append(MailSummary(uid=uid, **headers))

        results.sort(key=lambda m: _date_key(m.date), reverse=(order == "newest"))
        return results[:limit] if limit else results

    def fetch(self, folder_name: str, uid: str) -> MailMessage:
        """按 UID 取整封邮件并解析正文。"""
        folder = self.resolve_folder(folder_name)
        self._select(folder)
        typ, data = self.conn.uid("FETCH", uid, "(RFC822)")
        if typ != "OK" or not data or not isinstance(data[0], tuple):
            raise RuntimeError(f"读取邮件 UID={uid} 失败：{typ} {data}")
        return parse_message(data[0][1], uid=uid)

    def read_message(
        self,
        folder_name: str,
        title_contains: str | None = None,
        nth: int = 1,
        read_status: str = "unread",
        order: str = "newest",
    ) -> MailMessage | None:
        """核心接口：取指定文件夹里「第 nth 封」符合条件的邮件正文。

        :param folder_name:    文件夹名（必填）
        :param title_contains: 标题需包含的字符串，None 表示不过滤
        :param nth:            第几封，从 1 开始；配合 order 决定从新到旧还是从旧到新
        :param read_status:    "unread" 未读 / "read" 已读 / "all" 全部
        :param order:          "newest" 时 nth=1 表示最新一封，"oldest" 时表示最早一封
        :return:               MailMessage，找不到返回 None
        """
        if nth < 1:
            raise ValueError("nth 从 1 开始计数")
        if read_status not in READ_STATUS:
            raise ValueError(f"read_status 只能是 {list(READ_STATUS)}")

        matches = self.search(
            folder_name,
            read_status=read_status,
            title_contains=title_contains,
            order=order,
            limit=nth,
        )
        if len(matches) < nth:
            return None
        return self.fetch(folder_name, matches[nth - 1].uid)

    def message_count(self, folder_name: str) -> tuple[str | None, str | None]:
        """返回 (总数, 未读数)。"""
        folder = self.resolve_folder(folder_name)
        try:
            typ, data = self.conn.status(f'"{folder.raw}"', "(MESSAGES UNSEEN)")
        except Exception:
            return None, None
        if typ != "OK" or not data or not data[0]:
            return None, None
        text = data[0].decode("utf-8", "replace")
        return _stat_value(text, "MESSAGES"), _stat_value(text, "UNSEEN")

    # ---------------- 内部方法 ----------------
    def _search_uids(self, read_status: str) -> list[str]:
        criteria = READ_STATUS[read_status]
        typ, data = self.conn.uid("SEARCH", None, criteria)
        if typ != "OK" or not data or not data[0]:
            return []
        return [u.decode() for u in data[0].split()]

    def _fetch_headers(self, uids: Iterable[str]) -> Iterator[tuple[str, dict]]:
        uids = list(uids)
        if not uids:
            return
        typ, data = self.conn.uid("FETCH", ",".join(uids), HEADER_FIELDS)
        if typ != "OK":
            return
        for item in data or []:
            if not isinstance(item, tuple) or len(item) != 2:
                continue
            match = re.search(rb"UID (\d+)", item[0])
            if not match:
                continue
            yield match.group(1).decode(), parse_headers(item[1])


# ---------------- 辅助函数 ----------------
_ALIASES = {
    "inbox": "INBOX",
    "收件箱": "INBOX",
    "已发送": "Sent Messages",
    "sent": "Sent Messages",
    "sent messages": "Sent Messages",
    "草稿箱": "Drafts",
    "drafts": "Drafts",
    "已删除": "Deleted Messages",
    "deleted messages": "Deleted Messages",
    "垃圾箱": "Junk",
    "junk": "Junk",
}


def _parse_list_line(line: bytes) -> tuple[str, str, str]:
    """解析 LIST 一行：(\\HasNoChildren) "/" "INBOX" -> (flags, 分隔符, 原始名)"""
    text = line.decode("utf-8", "replace")
    flags = ""
    if text.startswith("("):
        end = text.find(")")
        if end != -1:
            flags, text = text[1:end], text[end + 1 :]
    text = text.strip()
    if not text:
        return flags, "/", ""

    if text.startswith('"'):
        end = text.find('"', 1)
        delimiter = text[1:end] if end != -1 else "/"
        rest = text[end + 1 :].strip()
    else:
        head, _, rest = text.partition(" ")
        delimiter = head

    if rest.startswith('"'):
        end = rest.rfind('"')
        raw = rest[1:end] if end > 0 else rest[1:]
    else:
        raw = rest.strip()
    return flags, delimiter, raw


def _date_key(text: str) -> float:
    """把 Date 头转成可排序的时间戳，解析失败排到最前（视为很早）。"""
    try:
        return parsedate_to_datetime(text).timestamp()
    except Exception:
        return 0.0


def _chunks(items: list[str], size: int) -> Iterator[list[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _stat_value(text: str, key: str) -> str | None:
    idx = text.find(key)
    if idx == -1:
        return None
    tokens = text[idx + len(key) :].replace(")", " ").split()
    return tokens[0] if tokens else None
