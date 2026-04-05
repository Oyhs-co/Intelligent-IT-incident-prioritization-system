"""Integration tests for metrics endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_metrics_overview(client: AsyncClient):
    """Test getting overview metrics."""
    response = await client.get("/api/v1/metrics/overview")
    assert response.status_code == 200

    data = response.json()
    assert "total_incidents_today" in data
    assert "total_incidents_week" in data
    assert "total_incidents_month" in data
    assert "incidents_open" in data
    assert "sla_compliance_rate" in data
    assert "processing_time_ms" in data


@pytest.mark.asyncio
async def test_metrics_sla(client: AsyncClient):
    """Test getting SLA metrics."""
    response = await client.get("/api/v1/metrics/sla")
    assert response.status_code == 200

    data = response.json()
    assert "overall_compliance_rate" in data
    assert "total_incidents" in data
    assert "breached_count" in data
    assert "met_count" in data
    assert "by_priority" in data


@pytest.mark.asyncio
async def test_metrics_ai(client: AsyncClient):
    """Test getting AI metrics."""
    response = await client.get("/api/v1/metrics/ai")
    assert response.status_code == 200

    data = response.json()
    assert "total_predictions" in data
    assert "avg_confidence" in data
    assert "confidence_distribution" in data


@pytest.mark.asyncio
async def test_metrics_incidents(client: AsyncClient):
    """Test getting incident metrics."""
    response = await client.get("/api/v1/metrics/incidents")
    assert response.status_code == 200

    data = response.json()
    assert "by_status" in data
    assert "by_priority" in data
    assert "by_category" in data
