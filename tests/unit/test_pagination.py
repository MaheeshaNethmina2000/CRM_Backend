import pytest
from app.util.pagination import normalize_pagination


@pytest.mark.unit
class TestNormalizePagination:

    def test_valid_inputs(self):
        page, limit, offset = normalize_pagination(2, 10)
        assert page == 2
        assert limit == 10
        assert offset == 10

    def test_zero_page_defaults_to_one(self):
        page, limit, offset = normalize_pagination(0, 10)
        assert page == 1
        assert offset == 0

    def test_negative_page_defaults_to_one(self):
        page, limit, offset = normalize_pagination(-5, 10)
        assert page == 1

    def test_zero_limit_defaults_to_ten(self):
        _, limit, _ = normalize_pagination(1, 0)
        assert limit == 10

    def test_limit_above_100_defaults_to_ten(self):
        _, limit, _ = normalize_pagination(1, 200)
        assert limit == 10

    def test_offset_calculation(self):
        _, _, offset = normalize_pagination(3, 20)
        assert offset == 40
