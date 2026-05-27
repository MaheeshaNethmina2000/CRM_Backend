from typing import Any, Optional


class GenericPaginationResponse:
    def __init__(
        self,
        is_error: bool,
        message: str,
        results: Optional[Any],
        status_code: int,
        total_records: int,
        page_number: int,
        page_size: int,
        total_pages: int,
    ):
        self.is_error = is_error
        self.message = message
        self.results = results
        self.status_code = status_code
        self.total_records = total_records
        self.page_number = page_number
        self.page_size = page_size
        self.total_pages = total_pages

    @classmethod
    def success(
        cls,
        message: str,
        results: Optional[Any],
        total_records: int,
        page_number: int,
        page_size: int,
        total_pages: int,
        status_code: int = 200,
    ):
        return cls(
            is_error=False,
            message=message,
            results=results,
            status_code=status_code,
            total_records=total_records,
            page_number=page_number,
            page_size=page_size,
            total_pages=total_pages,
        )

    @classmethod
    def failed(
        cls,
        message: str,
        results: Optional[Any],
        page_number: int,
        page_size: int,
        total_pages: int = 0,
        total_records: int = 0,
        status_code: int = 400,
    ):
        return cls(
            is_error=True,
            message=message,
            results=results,
            status_code=status_code,
            total_records=total_records,
            page_number=page_number,
            page_size=page_size,
            total_pages=total_pages,
        )

    def to_dict(self):
        return {
            "is_error": self.is_error,
            "message": self.message,
            "status_code": self.status_code,
            "total_records": self.total_records,
            "page_number": self.page_number,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
            "results": self.results,
        }
