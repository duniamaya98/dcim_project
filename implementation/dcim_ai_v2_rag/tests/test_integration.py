from fastapi.testclient import TestClient
from dcim_ai.api.inference_service import app

client = TestClient(app)

def test_predict_endpoint():
    response = client.post("/predict", json={
        "cpu_usage": 20,
        "memory_usage": 200,
        "disk_io": 20,
        "net_rx": 1000,
        "net_tx": 1000
    })

    assert response.status_code == 200
    assert "incident" in response.json()