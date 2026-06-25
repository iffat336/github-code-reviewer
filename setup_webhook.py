"""Register a signed GitHub pull-request webhook."""

import sys

from github import Auth, Github

from config import require_env


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python setup_webhook.py <public_url>")
        print("Example: python setup_webhook.py https://your-tunnel.example")
        return 1

    public_url = sys.argv[1].rstrip("/")
    github = Github(auth=Auth.Token(require_env("GITHUB_TOKEN")))
    repo = github.get_repo(require_env("GITHUB_REPO"))
    hook = repo.create_hook(
        name="web",
        config={
            "url": f"{public_url}/webhook",
            "content_type": "json",
            "secret": require_env("GITHUB_WEBHOOK_SECRET"),
            "insecure_ssl": "0",
        },
        events=["pull_request"],
        active=True,
    )

    print(f"Webhook created! ID: {hook.id}")
    print(f"Listening at: {public_url}/webhook")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
