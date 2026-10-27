"""Simple pagination helpers."""

from __future__ import annotations

from typing import Any


def paginate(items: list[Any], page: int, page_size: int) -> tuple[list[Any], int]:
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    total = len(items)
    start = (page - 1) * page_size
    return items[start : start + page_size], total
