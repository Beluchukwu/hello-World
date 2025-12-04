from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_case_lifecycle():
    create_resp = client.post(
        "/case",
        json={
            "client_id": "client-123",
            "tax_year": 2024,
            "primary_first_name": "Ada",
            "primary_last_name": "Lovelace",
            "filing_status": "single",
        },
    )
    assert create_resp.status_code == 201
    created_case = create_resp.json()
    case_id = created_case["metadata"]["id"]

    get_resp = client.get(f"/case/{case_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["taxpayer"]["primary"]["first_name"] == "Ada"

    patch_resp = client.patch(
        f"/case/{case_id}",
        json={"patch": {"taxpayer": {"filing_status": "married_filing_joint"}}},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["taxpayer"]["filing_status"] == "married_filing_joint"

    agent_resp = client.post(f"/tax-agent/{case_id}", json={"message": "Hello"})
    assert agent_resp.status_code == 200
    assert "reply" in agent_resp.json()
