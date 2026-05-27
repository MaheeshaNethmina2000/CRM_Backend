from typing import Tuple


def normalize_pagination(page: int, limit: int) -> Tuple[int, int, int]:
    page = page if page > 0 else 1
    limit = limit if 0 < limit <= 100 else 10
    offset = (page - 1) * limit
    return page, limit, offset
