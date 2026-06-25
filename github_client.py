"""GitHub API operations used by the reviewer."""

from github import Auth, Github

from config import require_env

REVIEW_MARKER = "<!-- autonomous-code-review-agent -->"


def get_github_client() -> Github:
    return Github(auth=Auth.Token(require_env("GITHUB_TOKEN")))


def get_repository():
    return get_github_client().get_repo(require_env("GITHUB_REPO"))


def get_pr_details(pr_number: int) -> dict:
    """Fetch PR metadata and changed-file patches."""
    pr = get_repository().get_pull(pr_number)
    files = [
        {
            "filename": changed_file.filename,
            "status": changed_file.status,
            "patch": changed_file.patch or "",
        }
        for changed_file in pr.get_files()
    ]
    return {
        "number": pr.number,
        "title": pr.title,
        "description": pr.body or "",
        "head_sha": pr.head.sha,
        "files": files,
    }


def post_review_comment(pr_number: int, review_body: str) -> None:
    """Create or update the agent's single review comment for a PR."""
    pr = get_repository().get_pull(pr_number)
    body = f"{REVIEW_MARKER}\n{review_body}"

    for comment in pr.get_issue_comments():
        if REVIEW_MARKER in (comment.body or ""):
            comment.edit(body)
            print(f"Review updated on PR #{pr_number}")
            return

    pr.create_issue_comment(body)
    print(f"Review posted on PR #{pr_number}")
