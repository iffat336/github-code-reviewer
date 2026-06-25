import hashlib
import hmac
import json
from unittest.mock import patch

from fastapi.testclient import TestClient

from webhook_server import app

client = TestClient(app)
SECRET = "test-webhook-secret"


def signed_headers(body: bytes, event: str = "pull_request") -> dict[str, str]:
    digest = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    return {
        "X-Hub-Signature-256": f"sha256={digest}",
        "X-GitHub-Event": event,
        "Content-Type": "application/json",
    }


def test_rejects_invalid_signature(monkeypatch):
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", SECRET)
    response = client.post(
        "/webhook",
        content=b"{}",
        headers={
            "X-Hub-Signature-256": "sha256=wrong",
            "X-GitHub-Event": "pull_request",
        },
    )
    assert response.status_code == 401


@patch("webhook_server.process_pr")
def test_accepts_synchronize_event(process_pr, monkeypatch):
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", SECRET)
    body = json.dumps(
        {
            "action": "synchronize",
            "pull_request": {"number": 42, "draft": False},
        }
    ).encode()

    response = client.post("/webhook", content=body, headers=signed_headers(body))

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    process_pr.assert_called_once_with(42)


def test_ignores_draft_pull_request(monkeypatch):
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", SECRET)
    body = json.dumps(
        {"action": "opened", "pull_request": {"number": 9, "draft": True}}
    ).encode()

    response = client.post("/webhook", content=body, headers=signed_headers(body))

    assert response.status_code == 200
    assert response.json() == {"status": "ignored", "reason": "draft pull request"}


def test_ignores_non_pull_request_event(monkeypatch):
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", SECRET)
    body = b"{}"
    response = client.post(
        "/webhook", content=body, headers=signed_headers(body, event="push")
    )
    assert response.json()["status"] == "ignored"
