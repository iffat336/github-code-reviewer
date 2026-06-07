from fastapi import FastAPI, Request, BackgroundTasks
from github_client import get_pr_details, post_review_comment
from reviewer_agent import review_code_with_claude
from rag_indexer import search_codebase
import uvicorn

app = FastAPI()

def process_pr(pr_number: int):
    """Full review pipeline — runs in background so webhook responds instantly."""
    try:
        print(f"\n[Agent] Reviewing PR #{pr_number}...")

        pr_details = get_pr_details(pr_number)
        print(f"[Agent] Fetched: {pr_details['title']}")

        query = f"{pr_details['title']} {pr_details['description']}"
        context = search_codebase(query)

        review = review_code_with_claude(pr_details, context)
        print("[Agent] Review generated.")

        post_review_comment(pr_number, review)
        print(f"[Agent] Review posted on PR #{pr_number}")

    except Exception as e:
        print(f"[Agent] Error reviewing PR #{pr_number}: {e}")

@app.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """GitHub calls this endpoint every time a PR is opened."""
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    if event == "pull_request" and payload.get("action") == "opened":
        pr_number = payload["pull_request"]["number"]
        print(f"\n[Webhook] New PR received: #{pr_number}")
        # Run review in background so GitHub doesn't timeout waiting
        background_tasks.add_task(process_pr, pr_number)

    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "GitHub Code Review Agent is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
