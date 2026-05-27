import pytest


@pytest.mark.integration
class TestHealthEndpoint:

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}


@pytest.mark.integration
class TestRootEndpoint:

    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200
