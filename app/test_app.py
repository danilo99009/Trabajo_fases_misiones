from app import app


def test_health_endpoint():
    """Prueba básica: el endpoint /health responde 200 sin necesidad de BD real."""
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"
