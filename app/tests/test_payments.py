from __future__ import annotations
import pytest
from httpx import AsyncClient


_VALID_PAYMENT = {
    "amount": 5000.00,
    "currency_from": "ZAR",
    "currency_to": "USD",
    "sender_country": "ZA",
    "receiver_country": "US",
    "sender_name": "Acme Corp",
    "receiver_name": "Global Supplier Inc",
    "payment_purpose": "Invoice settlement for goods",
    "routing_preference": "balanced",
    "urgency": 5,
    "risk_tolerance": 5,
}


@pytest.mark.anyio
async def test_process_payment_returns_200(client: AsyncClient):
    resp = await client.post("/api/v1/payment/process", json=_VALID_PAYMENT)
    assert resp.status_code == 200
    data = resp.json()
    assert "payment_id" in data
    assert "compliance_status" in data
    assert "selected_rail" in data
    assert "execution_status" in data


@pytest.mark.anyio
async def test_process_payment_rejected_zero_amount(client: AsyncClient):
    payload = {**_VALID_PAYMENT, "amount": 0}
    resp = await client.post("/api/v1/payment/process", json=payload)
    assert resp.status_code == 422  # Pydantic validation


@pytest.mark.anyio
async def test_process_payment_sanctioned_entity(client: AsyncClient):
    payload = {**_VALID_PAYMENT, "receiver_name": "SANCTIONED ENTITY LLC"}
    resp = await client.post("/api/v1/payment/process", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["compliance_status"] in ("REJECTED", "HOLD_FOR_REVIEW")


@pytest.mark.anyio
async def test_corridors_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/corridors")
    assert resp.status_code == 200
    data = resp.json()
    assert "ZA_ZA" in data or "ZA_US" in data


@pytest.mark.anyio
async def test_rails_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/rails")
    assert resp.status_code == 200
    data = resp.json()
    assert "rails" in data


@pytest.mark.anyio
async def test_metrics_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/metrics/session")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_payments" in data
