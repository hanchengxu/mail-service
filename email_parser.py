"""把 IMAP 返回的原始邮件字节解析成结构化对象。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from email import policy
from email.header import decode_header, make_header
from email.message import Message
from email.parser import BytesHeaderParser, BytesParser
from html import unescape


@dataclass
class MailMessage:
    uid: str = ""
    subject: str = ""
    sender: str = ""
    to: str = ""
    date: str = ""
    body_text: str = ""
    body_html: str = ""

    @property
    def body(self) -> str:
        """优先纯文本正文，没有则把 HTML 转成纯文本。"""
        return self.body_text or html_to_text(self.body_html)


def decode_mime_header(value) -> str:
    """解码 Subject/From 里的 =?utf-8?B?...?= 编码。"""
    if not value:
        return ""
    text = str(value)
    try:
        return str(make_header(decode_header(text))).strip()
    except Exception:
        return text.strip()


def parse_headers(raw: bytes) -> dict:
    """只解析头部，用于列表展示（比整封下载快很多）。"""
    msg = BytesHeaderParser(policy=policy.default).parsebytes(raw)
    return {
        "subject": decode_mime_header(msg.get("Subject")),
        "sender": decode_mime_header(msg.get("From")),
        "date": decode_mime_header(msg.get("Date")),
    }


def parse_message(raw: bytes, uid: str = "") -> MailMessage:
    """解析整封邮件（RFC822 原始字节）。"""
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    text, html = extract_body(msg)
    return MailMessage(
        uid=uid,
        subject=decode_mime_header(msg.get("Subject")),
        sender=decode_mime_header(msg.get("From")),
        to=decode_mime_header(msg.get("To")),
        date=decode_mime_header(msg.get("Date")),
        body_text=text,
        body_html=html,
    )


def extract_body(msg: Message) -> tuple[str, str]:
    """取出正文：返回 (纯文本, HTML)。"""
    text_parts: list[str] = []
    html_parts: list[str] = []

    parts = msg.walk() if msg.is_multipart() else [msg]
    for part in parts:
        if "attachment" in str(part.get("Content-Disposition") or "").lower():
            continue
        ctype = part.get_content_type()
        if ctype == "text/plain":
            text_parts.append(_decode_part(part))
        elif ctype == "text/html":
            html_parts.append(_decode_part(part))

    return "\n".join(p for p in text_parts if p).strip(), "\n".join(
        p for p in html_parts if p
    ).strip()


def html_to_text(html: str) -> str:
    """极简 HTML 转纯文本，避免为了取正文引入额外依赖。"""
    if not html:
        return ""
    text = re.sub(r"(?is)<(script|style)\b.*?>.*?</\1>", " ", html)
    text = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def _decode_part(part: Message) -> str:
    try:
        payload = part.get_payload(decode=True)
    except Exception:
        return ""
    if not payload:
        return ""
    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, "replace")
    except (LookupError, UnicodeDecodeError):
        return payload.decode("utf-8", "replace")
