from github import Github
from dotenv import load_dotenv
import os

load_dotenv()

def get_github_client():
    token = os.getenv("GITHUB_TOKEN")
    return Github(token)

def get_pr_details(pr_number: int):
    """Fetch PR title, description, and all changed files with diffs."""
    client = get_github_client()
    repo_name = os.getenv("GITHUB_REPO")
    repo = client.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    files = []
    for f in pr.get_files():
        files.append({
            "filename": f.filename,
            "status": f.status,        # added, modified, deleted
            "patch": f.patch or ""     # the actual code diff
        })

    return {
        "number": pr.number,
        "title": pr.title,
        "description": pr.body or "",
        "files": files
    }

def post_review_comment(pr_number: int, review_body: str):
    """Post a review comment on the PR."""
    client = get_github_client()
    repo_name = os.getenv("GITHUB_REPO")
    repo = client.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(review_body)
    print(f"Review posted on PR #{pr_number}")
