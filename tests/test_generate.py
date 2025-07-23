import pytest


@pytest.mark.asyncio
async def test_generate_endpoint(client):
    payload = {
        "prompt": "A red dragon flying over a mountain",
        "parameters": {"width": 512, "height": 512},
    }

    response = await client.post("/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_status_not_found(client):
    response = await client.get("/status/99999")
    assert response.status_code == 404
