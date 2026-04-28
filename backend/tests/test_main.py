from app.main import app


def test_health_check():
    response = app.test_client().get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
