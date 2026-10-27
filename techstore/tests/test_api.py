from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_get_pedido_inexistente():
    response = client.get("/orders/O030")
    assert response.status_code == 404

def test_confirmar_pedido_exitoso():
    response = client.post("/orders/O013/confirm")
    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"

def test_confirmar_pedido_dos_veces_conflict():
    client.post("/orders/O013/confirm")
    response = client.post("/orders/O013/confirm")
    assert response.status_code == 409