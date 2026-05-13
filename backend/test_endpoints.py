"""Prueba automatizada de los endpoints del sistema.

Uso:
    python test_endpoints.py                          # usa http://localhost:8000
    python test_endpoints.py --base-url http://localhost:8000
    python test_endpoints.py --verbose
"""

import asyncio
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx

BASE_URL = "http://localhost:8000"
VERBOSE = False
SHOW_DATA = True


@dataclass
class TestState:
    tokens: dict[str, Any] = field(default_factory=dict)
    user_id: str | None = None
    incident_id: str | None = None
    comment_id: str | None = None


state = TestState()


async def _request_root():
    ok, data = await request("GET", "/", expect=200)
    if ok:
        show_data("API Info", data, ["name", "version", "status"])
    return ok


# ── helpers ──────────────────────────────────────────────────────────


def _fmt(val: Any, indent: int = 0) -> str:
    pad = "  " * indent
    if val is None:
        return "None"
    if isinstance(val, bool):
        return "yes" if val else "no"
    if isinstance(val, float):
        return f"{val:.4f}"
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d %H:%M UTC")
    if isinstance(val, dict):
        lines = []
        for k, v in val.items():
            lines.append(f"{pad}{k}: {_fmt(v, indent)}")
        return "\n".join(lines)
    if isinstance(val, list):
        if not val:
            return "[]"
        items = ", ".join(str(v) if len(str(v)) < 60 else str(v)[:57] + "..." for v in val)
        return f"[{items}]"
    return str(val)


def show(key: str, val: Any):
    """Print a single readable key: value line."""
    if SHOW_DATA:
        print(f"         {key}: {_fmt(val)}")


def show_data(label: str, data: dict, fields: list[str] | None = None):
    """Print response data in readable format, optionally filtering fields."""
    if not SHOW_DATA or not data:
        return
    print(f"         --- {label} ---")
    keys = fields or list(data.keys())
    for k in keys:
        if k in data:
            print(f"         {k}: {_fmt(data[k])}")



def log(msg: str, ok: bool = True):
    icon = "PASS" if ok else "FAIL"
    print(f"  [{icon}] {msg}")


def fail(msg: str) -> bool:
    print(f"  [FAIL] {msg}")
    return False


async def request(
    method: str,
    path: str,
    expect: int = 200,
    json: dict | None = None,
    token: str | None = None,
) -> tuple[bool, dict | None]:
    url = f"{BASE_URL}{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(method, url, json=json, headers=headers)
    except httpx.ConnectError:
        return fail(f"Connection refused at {BASE_URL} — is the server running?"), None
    except Exception as e:
        return fail(f"Request error: {e}"), None

    ok = resp.status_code == expect
    detail = ""
    try:
        data = resp.json()
        if not ok:
            detail = data.get("detail") or data.get("error") or str(data)
    except Exception:
        data = None
        detail = resp.text[:200]

    if not ok:
        return fail(f"{method} {path} => {resp.status_code} (expected {expect}): {detail}"), data

    if VERBOSE:
        log(f"{method} {path} => {resp.status_code}")
    return True, data


# ── tests ─────────────────────────────────────────────────────────────


async def test_health():
    """GET /health and GET /"""
    ok, data = await request("GET", "/health")
    if ok:
        assert data["status"] == "healthy"
        show_data("Health", data, ["status"])
    _ok, _data = await request("GET", "/")
    if _ok:
        assert _data["status"] == "running"
        show_data("Root", _data, ["name", "version", "status"])
    return ok


async def test_register():
    """POST /api/v1/auth/register"""
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": email,
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "password": "SecurePass123!",
        "first_name": "Test",
        "last_name": "User",
        "department": "IT",
    }
    ok, data = await request("POST", "/api/v1/auth/register", json=payload, expect=201)
    if ok:
        assert data["email"] == email
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert "id" in data
        state.user_id = data["id"]
        show_data("User created", data, ["email", "username", "role", "first_name", "last_name", "department", "id"])
    return ok


async def test_register_duplicate():
    """POST /api/v1/auth/register with duplicate email => 400"""
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "username": f"dup_{uuid.uuid4().hex[:8]}", "password": "SecurePass123!"}
    r1, d1 = await request("POST", "/api/v1/auth/register", json=payload, expect=201)
    show_data("First user", d1, ["email", "username"])
    # duplicate email, different username
    payload2 = {"email": email, "username": f"dup2_{uuid.uuid4().hex[:8]}", "password": "SecurePass123!"}
    ok, d2 = await request("POST", "/api/v1/auth/register", json=payload2, expect=400)
    if ok:
        show("expected_error", d2.get("detail") or d2.get("error", "duplicate rejected"))
    return ok


async def test_login():
    """POST /api/v1/auth/login"""
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePass123!"
    await request("POST", "/api/v1/auth/register", json={
        "email": email, "username": f"login_{uuid.uuid4().hex[:8]}", "password": pwd,
    }, expect=201)

    ok, data = await request("POST", "/api/v1/auth/login", json={"email": email, "password": pwd})
    if ok:
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        state.tokens = data
        show_data("Login", data, ["token_type", "expires_in"])
        show("access_token", data["access_token"][:40] + "...")
        show("refresh_token", data["refresh_token"][:40] + "...")
    return ok


async def test_login_invalid():
    """POST /api/v1/auth/login with bad credentials => 401"""
    ok, data = await request("POST", "/api/v1/auth/login", json={
        "email": "noone@nonexistent.com", "password": "wrong",
    }, expect=401)
    if ok:
        show("expected_error", data.get("detail", "Invalid credentials"))
    return ok


async def test_refresh_token():
    """POST /api/v1/auth/refresh"""
    if not state.tokens.get("refresh_token"):
        return fail("No refresh token available")
    ok, data = await request("POST", "/api/v1/auth/refresh", json={
        "refresh_token": state.tokens["refresh_token"],
    })
    if ok:
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        show("new_access_token", data["access_token"][:40] + "...")
    return ok


async def test_refresh_invalid():
    """POST /api/v1/auth/refresh with invalid token => 401"""
    ok, data = await request("POST", "/api/v1/auth/refresh", json={
        "refresh_token": "this_is_totally_invalid",
    }, expect=401)
    if ok:
        show("expected_error", data.get("detail", "invalid token"))
    return ok


async def test_get_me():
    """GET /api/v1/auth/me"""
    if not state.tokens.get("access_token"):
        return fail("No access token")
    ok, data = await request("GET", "/api/v1/auth/me", token=state.tokens["access_token"])
    if ok:
        assert "email" in data
        assert "username" in data
        show_data("Current user", data, ["email", "username", "role", "full_name", "department", "is_active"])
    return ok


async def test_get_me_unauthorized():
    """GET /api/v1/auth/me without token => 401"""
    ok, data = await request("GET", "/api/v1/auth/me", expect=401)
    if ok:
        show("expected_error", data.get("detail", "not authenticated"))
    return ok


async def test_list_users():
    """GET /api/v1/users/"""
    ok, data = await request("GET", "/api/v1/users/")
    if ok:
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        show("total_users", data["total"])
        for u in data["items"][:3]:
            show_data("User", u, ["email", "username", "role"])
    return ok


async def test_get_user():
    """GET /api/v1/users/{id}"""
    if not state.user_id:
        return fail("No user id available")
    ok, data = await request("GET", f"/api/v1/users/{state.user_id}")
    if ok:
        assert data["id"] == state.user_id
        show_data("User", data, ["email", "username", "role", "full_name", "department", "is_active"])
    return ok


async def test_get_user_not_found():
    """GET /api/v1/users/{fake_id} => 404"""
    ok, data = await request("GET", f"/api/v1/users/{uuid.uuid4()}", expect=404)
    if ok:
        show("expected_error", data.get("detail", "not found"))
    return ok


async def test_update_user():
    """PUT /api/v1/users/{id}"""
    if not state.user_id or not state.tokens.get("access_token"):
        return fail("Missing user id or token")
    ok, data = await request("PUT", f"/api/v1/users/{state.user_id}", json={
        "first_name": "UpdatedName",
        "department": "Engineering",
    }, token=state.tokens["access_token"])
    if ok:
        assert data["first_name"] == "UpdatedName"
        assert data["department"] == "Engineering"
        show_data("Updated user", data, ["email", "username", "first_name", "last_name", "department", "role"])
    return ok


async def test_create_incident():
    """POST /api/v1/incidents/"""
    payload = {
        "title": "Test Incident - Cannot access email",
        "description": "User reports unable to access Outlook email client after password reset",
        "category": "software",
        "subcategory": "email",
        "urgency": 4,
        "impact": 3,
    }
    ok, data = await request("POST", "/api/v1/incidents/", json=payload, expect=201,
                             token=state.tokens.get("access_token"))
    if ok:
        assert data["title"] == payload["title"]
        assert data["status"] == "new"
        assert "id" in data
        assert "ticket_number" in data
        state.incident_id = data["id"]
        show_data("Incident created", data, ["ticket_number", "title", "status", "priority", "urgency", "impact", "category", "id"])
    return ok


async def test_create_incident_validation_error():
    """POST /api/v1/incidents/ with empty title => 422"""
    ok, data = await request("POST", "/api/v1/incidents/", json={
        "title": "", "description": "test",
    }, expect=422)
    if ok:
        show("expected_error", data.get("detail", data.get("error", "validation error")))
    return ok


async def test_list_incidents():
    """GET /api/v1/incidents/"""
    ok, data = await request("GET", "/api/v1/incidents/")
    if ok:
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
        show("total_incidents", data["total"])
        for inc in data["items"][:3]:
            show_data("Incident", inc, ["ticket_number", "title", "status", "priority", "category"])
    return ok


async def test_list_incidents_filtered():
    """GET /api/v1/incidents/?status=new&limit=5"""
    ok, data = await request("GET", "/api/v1/incidents/", expect=200)
    if ok:
        ok, data = await request("GET", "/api/v1/incidents/?status=new&limit=5")
        if ok:
            assert "items" in data
            show("incidents_filtered", len(data["items"]))
    return ok


async def test_get_incident():
    """GET /api/v1/incidents/{id}"""
    if not state.incident_id:
        return fail("No incident id")
    ok, data = await request("GET", f"/api/v1/incidents/{state.incident_id}")
    if ok:
        assert data["id"] == state.incident_id
        assert data["title"] is not None
        show_data("Incident detail", data, ["ticket_number", "title", "description", "status", "priority", "priority_label", "urgency", "impact", "category", "source", "created_at"])
    return ok


async def test_get_incident_not_found():
    """GET /api/v1/incidents/{fake_id} => 404"""
    ok, data = await request("GET", f"/api/v1/incidents/{uuid.uuid4()}", expect=404)
    if ok:
        show("expected_error", data.get("detail", "not found"))
    return ok


async def test_update_incident():
    """PUT /api/v1/incidents/{id}"""
    if not state.incident_id or not state.tokens.get("access_token"):
        return fail("Missing incident id or token")
    ok, data = await request("PUT", f"/api/v1/incidents/{state.incident_id}", json={
        "title": "Updated: Cannot access email",
        "description": "Issue resolved after password reset",
        "status": "in_progress",
    }, token=state.tokens["access_token"])
    if ok:
        assert data["title"] == "Updated: Cannot access email"
        assert data["status"] == "in_progress"
        show_data("Incident updated", data, ["ticket_number", "title", "status", "priority", "updated_at"])
    return ok


async def test_update_incident_not_found():
    """PUT /api/v1/incidents/{fake_id} => 404"""
    ok, data = await request("PUT", f"/api/v1/incidents/{uuid.uuid4()}", json={
        "title": "Nope",
    }, token=state.tokens.get("access_token"), expect=404)
    if ok:
        show("expected_error", data.get("detail", "not found"))
    return ok


async def test_classify_incident():
    """POST /api/v1/incidents/{id}/classify"""
    if not state.incident_id or not state.tokens.get("access_token"):
        return fail("Missing incident id or token")
    ok, data = await request("POST", f"/api/v1/incidents/{state.incident_id}/classify",
                             token=state.tokens["access_token"])
    if ok:
        assert data["incident_id"] == state.incident_id
        assert "priority" in data
        assert "confidence" in data
        assert "explanation" in data
        show_data("Classification", data, ["priority", "priority_label", "confidence", "explanation", "top_features", "processing_time_ms"])
    return ok


async def test_get_recommendations():
    """POST /api/v1/incidents/{id}/recommendations"""
    if not state.incident_id or not state.tokens.get("access_token"):
        return fail("Missing incident id or token")
    ok, data = await request("POST", f"/api/v1/incidents/{state.incident_id}/recommendations",
                             token=state.tokens["access_token"])
    if ok:
        assert "incident_id" in data
        assert "recommended_priority" in data
        assert "suggested_actions" in data
        show_data("Recommendations", data, ["recommended_priority", "recommended_priority_label", "confidence", "similar_incidents_count", "avg_resolution_time_hours", "suggested_actions", "explanation"])
    return ok


async def test_get_recommendations_not_found():
    """POST /api/v1/incidents/{fake_id}/recommendations => 404"""
    ok, data = await request("POST", f"/api/v1/incidents/{uuid.uuid4()}/recommendations",
                          token=state.tokens.get("access_token"), expect=404)
    if ok:
        show("expected_error", data.get("detail", "not found"))
    return ok


async def test_search_similar():
    """POST /api/v1/incidents/similar"""
    ok, data = await request("POST", "/api/v1/incidents/similar", json={
        "query": "Email access issue after password reset",
        "limit": 5,
        "min_similarity": 0.0,
    }, token=state.tokens.get("access_token"))
    if ok:
        assert "items" in data
        assert "total" in data
        show("total_similar", data["total"])
        for item in data["items"][:3]:
            show_data("Match", item, ["ticket_number", "title", "similarity_score", "status", "priority_label"])
    return ok


async def test_get_incident_events():
    """GET /api/v1/incidents/{id}/events"""
    if not state.incident_id:
        return fail("No incident id")
    ok, data = await request("GET", f"/api/v1/incidents/{state.incident_id}/events",
                             token=state.tokens.get("access_token"))
    if ok:
        assert isinstance(data, list)
        show("total_events", len(data))
        for ev in data[:3]:
            show_data("Event", ev, ["event_type", "old_value", "new_value", "created_at"])
    return ok


async def test_add_comment():
    """POST /api/v1/incidents/{id}/comments"""
    if not state.incident_id or not state.tokens.get("access_token"):
        return fail("Missing incident id or token")
    ok, data = await request("POST", f"/api/v1/incidents/{state.incident_id}/comments", json={
        "content": "Contacting user to verify access has been restored",
        "is_internal": False,
    }, expect=201, token=state.tokens["access_token"])
    if ok:
        assert data["content"] == "Contacting user to verify access has been restored"
        assert data["is_internal"] is False
        state.comment_id = data["id"]
        show_data("Comment added", data, ["content", "is_internal", "created_at"])
    return ok


async def test_add_internal_comment():
    """POST /api/v1/incidents/{id}/comments (internal)"""
    if not state.incident_id or not state.tokens.get("access_token"):
        return fail("Missing incident id or token")
    ok, data = await request("POST", f"/api/v1/incidents/{state.incident_id}/comments", json={
        "content": "Internal note: escalated to senior team",
        "is_internal": True,
    }, expect=201, token=state.tokens["access_token"])
    if ok:
        assert data["is_internal"] is True
        show_data("Internal comment", data, ["content", "is_internal", "created_at"])
    return ok


async def test_list_comments():
    """GET /api/v1/incidents/{id}/comments"""
    if not state.incident_id:
        return fail("No incident id")
    ok, data = await request("GET", f"/api/v1/incidents/{state.incident_id}/comments?include_internal=true",
                             token=state.tokens.get("access_token"))
    if ok:
        assert isinstance(data, list)
        assert len(data) >= 2
        show("total_comments", len(data))
        for c in data[:2]:
            show_data("Comment", c, ["content", "is_internal", "created_at"])
    return ok


async def test_metrics_overview():
    """GET /api/v1/metrics/overview"""
    ok, data = await request("GET", "/api/v1/metrics/overview")
    if ok:
        for field in ("total_incidents_today", "incidents_open", "sla_compliance_rate",
                      "active_users", "model_confidence_avg"):
            assert field in data, f"Missing field: {field}"
        show_data("Overview", data, ["total_incidents_today", "total_incidents_week", "total_incidents_month", "incidents_open", "incidents_in_progress", "incidents_resolved", "incidents_closed", "avg_response_time_minutes", "avg_resolution_time_minutes", "sla_compliance_rate", "sla_breach_count", "model_accuracy", "model_confidence_avg", "ai_predictions_today", "active_users", "active_technicians"])
    return ok


async def test_metrics_incidents():
    """GET /api/v1/metrics/incidents"""
    ok, data = await request("GET", "/api/v1/metrics/incidents")
    if ok:
        assert "by_status" in data
        assert "by_priority" in data
        assert "by_category" in data
        show("by_status", data["by_status"])
        show("by_priority", data["by_priority"])
        show("by_category", data["by_category"])
    return ok


async def test_metrics_ai():
    """GET /api/v1/metrics/ai"""
    ok, data = await request("GET", "/api/v1/metrics/ai")
    if ok:
        assert "total_predictions" in data
        assert "avg_confidence" in data
        assert "confidence_distribution" in data
        show_data("AI Metrics", data, ["total_predictions", "accuracy", "avg_confidence", "confidence_distribution"])
    return ok


async def test_metrics_sla():
    """GET /api/v1/metrics/sla"""
    ok, data = await request("GET", "/api/v1/metrics/sla")
    if ok:
        assert "overall_compliance_rate" in data
        assert "total_incidents" in data
        assert "by_priority" in data
        show_data("SLA Metrics", data, ["overall_compliance_rate", "total_incidents", "breached_count", "met_count", "avg_resolution_time_minutes", "at_risk_incidents"])
    return ok


async def test_metrics_health():
    """GET /api/v1/metrics/health"""
    ok, data = await request("GET", "/api/v1/metrics/health")
    if ok:
        assert "status" in data
        assert "version" in data
        assert "database" in data
        show_data("Health", data, ["status", "version", "database", "ai_model", "timestamp"])
    return ok


async def test_delete_incident():
    """DELETE /api/v1/incidents/{id}"""
    if not state.tokens.get("access_token"):
        return fail("No access token")
    # create temp incident to delete
    ok, data = await request("POST", "/api/v1/incidents/", json={
        "title": "Temp Incident for Deletion",
        "description": "This will be deleted",
        "urgency": 2, "impact": 2,
    }, expect=201, token=state.tokens["access_token"])
    if not ok:
        return fail("Could not create temp incident")
    temp_id = data["id"]
    show("deleting_incident", temp_id)

    ok, _ = await request("DELETE", f"/api/v1/incidents/{temp_id}",
                          expect=204, token=state.tokens["access_token"])
    if ok:
        ok2, d2 = await request("GET", f"/api/v1/incidents/{temp_id}", expect=404)
        if not ok2:
            return fail("Incident still exists after deletion")
        show("deleted", "confirmed (GET returned 404)")
    return ok


async def test_delete_incident_not_found():
    """DELETE /api/v1/incidents/{fake_id} => 404"""
    ok, data = await request("DELETE", f"/api/v1/incidents/{uuid.uuid4()}",
                          token=state.tokens.get("access_token"), expect=404)
    if ok:
        show("expected_error", data.get("detail", "not found"))
    return ok


async def test_delete_user():
    """DELETE /api/v1/users/{id}"""
    if not state.tokens.get("access_token"):
        return fail("No access token")
    email = f"del_{uuid.uuid4().hex[:8]}@example.com"
    ok, data = await request("POST", "/api/v1/auth/register", json={
        "email": email, "username": f"del_{uuid.uuid4().hex[:8]}", "password": "SecurePass123!",
    }, expect=201)
    if not ok:
        return fail("Could not create temp user")
    del_user_id = data["id"]
    show("deleting_user", del_user_id)

    ok, _ = await request("DELETE", f"/api/v1/users/{del_user_id}",
                          expect=204, token=state.tokens["access_token"])
    if ok:
        ok2, d2 = await request("GET", f"/api/v1/users/{del_user_id}", expect=404)
        if not ok2:
            return fail("User still exists after deletion")
        show("deleted", "confirmed (GET returned 404)")
    return ok


async def test_delete_user_not_found():
    """DELETE /api/v1/users/{fake_id} => 404"""
    ok, data = await request("DELETE", f"/api/v1/users/{uuid.uuid4()}",
                          token=state.tokens.get("access_token"), expect=404)
    if ok:
        show("expected_error", data.get("detail", "not found"))
    return ok


# ── test runner ───────────────────────────────────────────────────────

TESTS = [
    ("Health Check", test_health),
    ("Root Endpoint", _request_root),

    # Auth
    ("Register User", test_register),
    ("Register Duplicate Email", test_register_duplicate),
    ("Login Success", test_login),
    ("Login Invalid Credentials", test_login_invalid),
    ("Refresh Token", test_refresh_token),
    ("Refresh Invalid Token", test_refresh_invalid),
    ("Get Current User", test_get_me),
    ("Get Current User Unauthorized", test_get_me_unauthorized),
    # Users CRUD
    ("List Users", test_list_users),
    ("Get User By ID", test_get_user),
    ("Get User Not Found", test_get_user_not_found),
    ("Update User", test_update_user),
    # Incidents CRUD
    ("Create Incident", test_create_incident),
    ("Create Incident Validation Error", test_create_incident_validation_error),
    ("List Incidents", test_list_incidents),
    ("List Incidents Filtered", test_list_incidents_filtered),
    ("Get Incident", test_get_incident),
    ("Get Incident Not Found", test_get_incident_not_found),
    ("Update Incident", test_update_incident),
    ("Update Incident Not Found", test_update_incident_not_found),
    # Incident Actions
    ("Classify Incident", test_classify_incident),
    ("Get Recommendations", test_get_recommendations),
    ("Get Recommendations Not Found", test_get_recommendations_not_found),
    ("Search Similar Incidents", test_search_similar),
    ("Get Incident Events", test_get_incident_events),
    # Comments
    ("Add Comment", test_add_comment),
    ("Add Internal Comment", test_add_internal_comment),
    ("List Comments", test_list_comments),
    # Metrics
    ("Metrics Overview", test_metrics_overview),
    ("Metrics Incidents", test_metrics_incidents),
    ("Metrics AI", test_metrics_ai),
    ("Metrics SLA", test_metrics_sla),
    ("Metrics Health", test_metrics_health),
    # Delete
    ("Delete Incident", test_delete_incident),
    ("Delete Incident Not Found", test_delete_incident_not_found),
    ("Delete User", test_delete_user),
    ("Delete User Not Found", test_delete_user_not_found),
]


async def run_all():
    passed = 0
    failed = 0
    total = len(TESTS)
    results: list[tuple[str, bool, float]] = []

    print(f"\n{'='*60}")
    print(f"  Endpoint Tests - {BASE_URL}")
    print(f"{'='*60}\n")

    for name, test_fn in TESTS:
        print(f"  {name}... ", end="")
        sys.stdout.flush()
        start = time.perf_counter()
        try:
            if asyncio.iscoroutinefunction(test_fn):
                ok = await test_fn()
            else:
                ok = test_fn()
        except Exception as e:
            ok = False
            print(f"  [FAIL] Exception: {e}")
        elapsed = (time.perf_counter() - start) * 1000
        results.append((name, ok, elapsed))
        if ok:
            passed += 1
        else:
            failed += 1
        status = "PASS" if ok else "FAIL"
        print(f"\r  [{status}] {name} ({elapsed:.0f}ms)")
        sys.stdout.flush()

    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} passed, {failed} failed")
    if failed:
        print("\n  Failed tests:")
        for name, ok, _ in results:
            if not ok:
                print(f"    - {name}")
    print(f"{'='*60}\n")

    return failed == 0


def main():
    import argparse

    global BASE_URL, VERBOSE

    parser = argparse.ArgumentParser(description="Test API endpoints")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    BASE_URL = args.base_url.rstrip("/")
    VERBOSE = args.verbose

    success = asyncio.run(run_all())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
