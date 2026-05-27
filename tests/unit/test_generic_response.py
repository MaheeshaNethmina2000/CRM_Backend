import pytest
from app.model.generic_response import GenericResponse
from app.model.generic_pagination_response import GenericPaginationResponse


@pytest.mark.unit
class TestGenericResponse:

    def test_success_response(self):
        response = GenericResponse.success(message="OK", results={"id": 1})
        assert response.is_error is False
        assert response.status_code == 200
        assert response.results == {"id": 1}

    def test_failed_response(self):
        response = GenericResponse.failed(message="Not found", results=[], status_code=404)
        assert response.is_error is True
        assert response.status_code == 404

    def test_to_dict_keys(self):
        response = GenericResponse.success(message="OK", results=[])
        d = response.to_dict()
        assert set(d.keys()) == {"is_error", "message", "status_code", "results"}


@pytest.mark.unit
class TestGenericPaginationResponse:

    def test_success_pagination(self):
        response = GenericPaginationResponse.success(
            message="OK",
            results=[1, 2, 3],
            total_records=3,
            page_number=1,
            page_size=10,
            total_pages=1,
        )
        assert response.is_error is False
        assert response.total_records == 3
        assert response.total_pages == 1

    def test_to_dict_contains_pagination_keys(self):
        response = GenericPaginationResponse.success(
            message="OK", results=[], total_records=0,
            page_number=1, page_size=10, total_pages=0,
        )
        d = response.to_dict()
        assert "total_records" in d
        assert "page_number" in d
        assert "page_size" in d
        assert "total_pages" in d
