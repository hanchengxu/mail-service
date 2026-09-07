"""IMAP modified UTF-7 编解码 (RFC 3501)。

Python 没有内置该编解码器，但 IMAP 里非 ASCII 的文件夹名用的就是它，
例如「已发送」在网络上表现为 &UXZO1mWHTvZZOQ-，不解码就会显示成一串乱码。
"""

from __future__ import annotations

import base64


def imap_utf7_decode(name: str) -> str:
    """'&UXZO1mWHTvZZOQ-' -> '已发送'"""
    if "&" not in name:
        return name

    out: list[str] = []
    buf: str | None = None
    for ch in name:
        if buf is None:
            if ch == "&":
                buf = ""
            else:
                out.append(ch)
        elif ch == "-":
            out.append("&" if buf == "" else _b64_decode_utf16be(buf))
            buf = None
        else:
            buf += ch
    if buf is not None:
        out.append("&" + buf)  # 格式异常，原样保留
    return "".join(out)


def imap_utf7_encode(text: str) -> str:
    """'已发送' -> '&UXZO1mWHTvZZOQ-'，用于把中文文件夹名发给服务器。"""
    out: list[str] = []
    pending: list[str] = []

    def flush() -> None:
        if not pending:
            return
        raw = "".join(pending).encode("utf-16-be")
        token = base64.b64encode(raw).decode("ascii").rstrip("=").replace("/", ",")
        out.append(f"&{token}-")
        pending.clear()

    for ch in text:
        if ch == "&":
            flush()
            out.append("&-")
        elif 0x20 <= ord(ch) <= 0x7E:  # 可打印 ASCII 原样保留
            flush()
            out.append(ch)
        else:
            pending.append(ch)
    flush()
    return "".join(out)


def _b64_decode_utf16be(payload: str) -> str:
    data = payload.replace(",", "/")
    pad = "=" * (-len(data) % 4)
    try:
        return base64.b64decode(data + pad).decode("utf-16-be")
    except Exception:
        return "&" + payload + "-"
