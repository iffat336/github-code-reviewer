"""
Registers a webhook on the GitHub repo so it notifies this agent
every time a new Pull Request is opened.

Usage: python setup_webhook.py <ngrok_or_public_url>
Example: python setup_webhook.py https://your-tunnel.ngrok-free.dev
"""
import sys
import os
from github import Github, Auth
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python setup_webhook.py <public_url>")
    print("Example: python setup_webhook.py https://your-tunnel.ngrok-free.dev")
    sys.exit(1)

PUBLIC_URL = sys.argv[1].rstrip("/")

token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPO")

g = Github(auth=Auth.Token(token))
repo = g.get_repo(repo_name)

hook = repo.create_hook(
    name="web",
    config={
        "url": f"{PUBLIC_URL}/webhook",
        "content_type": "json"
    },
    events=["pull_request"],
    active=True
)

print(f"Webhook created! ID: {hook.id}")
print(f"Listening at: {PUBLIC_URL}/webhook")
print("GitHub will now call this URL every time a PR is opened.")
