"""Text-file decoding helpers for Windows-authored article files."""

from __future__ import annotations

from pathlib import Path


def decode_text(data: bytes) -> str:
    """Decode UTF-8/UTF-16 files and fall back to GB18030 for legacy files."""
    if data.startswith(b"\xef\xbb\xbf"):
        return data[3:].decode("utf-8")
    if data.startswith(b"\xff\xfe"):
        return data[2:].decode("utf-16-le")
    if data.startswith(b"\xfe\xff"):
        return data[2:].decode("utf-16-be")
    try:
        return data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return data.decode("gb18030")


def read_text(path: str | Path) -> str:
    return decode_text(Path(path).read_bytes())
