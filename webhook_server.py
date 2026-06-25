"""FastAPI webhook service for autonomous pull-request reviews."""

import hashlib
import hmac
import json
import logging

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request

from config import require_env
from github_client import get_pr_details, post_review_comment
from rag_indexer import search_codebase
from reviewer_agent import review_code_with_claude

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Autonomous GitHub Code Review Agent")
SUPPORTED_ACTIONS = {"opened", "reopened", "synchronize", "ready_for_review"}


def verify_github_signature(body: bytes, signature: str | None) -> bool:
    """Verify GitHub's HMAC-SHA256 webhook signature."""
    if not signature or not signature.startswith("sha256="):
        return False
    secret = require_env("GITHUB_WEBHOOK_SECRET").encode("utf-8")
    expected = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def process_pr(pr_number: int) -> None:
    """Run the complete review pipeline in a background task."""
    try:
        logger.info("Reviewing PR #%s", pr_number)
        pr_details = get_pr_details(pr_number)
        query = f"{pr_details['title']} {pr_details['description']}"
        context = search_codebase(query)
        review = review_code_with_claude(pr_details, context)
        post_review_comment(pr_number, review)
        logger.info("Review completed for PR #%s", pr_number)
    except Exception:
        logger.exception("Error reviewing PR #%s", pr_number)


@app.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """Validate and enqueue supported GitHub pull-request events."""
    body = await request.body()
    try:
        signature_valid = verify_github_signature(
            body, request.headers.get("X-Hub-Signature-256")
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not signature_valid:
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    if request.headers.get("X-GitHub-Event") != "pull_request":
        return {"status": "ignored", "reason": "unsupported event"}

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    action = payload.get("action")
    if action not in SUPPORTED_ACTIONS:
        return {"status": "ignored", "reason": "unsupported action"}

    pull_request = payload.get("pull_request") or {}
    if pull_request.get("draft"):
        return {"status": "ignored", "reason": "draft pull request"}

    pr_number = pull_request.get("number")
    if not isinstance(pr_number, int):
        raise HTTPException(status_code=400, detail="Missing pull request number")

    background_tasks.add_task(process_pr, pr_number)
    logger.info("Accepted %s event for PR #%s", action, pr_number)
    return {"status": "accepted", "pr_number": pr_number, "action": action}


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok", "service": "github-code-reviewer"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
