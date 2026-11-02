"""API tests. The printer is faked; no real network I/O happens."""
import openapi_server
from tests.conftest import FakePrinter


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["name"] == "TicketGremlin API"


def test_health_healthy(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
    assert r.json()["printer"] == "connected"


def test_health_degraded_returns_503(client, monkeypatch):
    monkeypatch.setattr(openapi_server, "_test_printer_connection", lambda: False)
    r = client.get("/health")
    assert r.status_code == 503
    assert r.json()["status"] == "degraded"


def test_cors_wildcard_without_credentials(client):
    r = client.get("/health", headers={"Origin": "http://example.local"})
    assert r.headers["access-control-allow-origin"] == "*"
    assert "access-control-allow-credentials" not in r.headers


def test_print_message(client, fake_printer):
    r = client.post("/print_message", json={"title": "T", "message": "hello"})
    assert r.status_code == 200
    assert r.json()["status"] == "success"
    assert fake_printer.device.calls == ["open", "printMessage", "cut", "close"]


def test_print_message_failure_still_closes(failing_printer):
    from fastapi.testclient import TestClient
    c = TestClient(openapi_server.app)
    r = c.post("/print_message", json={"title": "T", "message": "hello"})
    assert r.status_code == 500
    assert "close" in failing_printer.device.calls


def test_print_message_formatting_error_is_422(client, monkeypatch):
    class BadMessage:
        def __init__(self, **kw):
            raise ValueError("bad body")

    monkeypatch.setattr(openapi_server, "Message", BadMessage)
    r = client.post("/print_message", json={"title": "T", "message": "x"})
    assert r.status_code == 422
    assert "bad body" in r.json()["detail"]


def test_print_task(client, fake_printer):
    r = client.post("/print_task", json={
        "title": "T", "message": "m", "due_date": "ASAP"})
    assert r.status_code == 200
    assert r.json()["due_date"] == "ASAP"


def test_feed_cut_no_body(client, fake_printer):
    r = client.post("/feed_cut")
    assert r.status_code == 200
    assert fake_printer.device.calls == ["open", "ln", "cut", "close"]


def test_print_config_no_body(client, fake_printer):
    r = client.post("/print_config")
    assert r.status_code == 200
    assert "close" in fake_printer.device.calls


def test_print_image_removed(client):
    r = client.post("/print_image", json={"filepath": "/tmp/x.jpg"})
    assert r.status_code == 404


def test_openapi_spec(client):
    spec = client.get("/openapi.json").json()
    assert "/print_image" not in spec["paths"]
    assert spec["paths"]["/print_message"]["post"]["operationId"] == "print_message"
    assert spec["paths"]["/health"]["get"]["operationId"] == "health"
