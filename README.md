# Autonomous GitHub Code Review Agent

An AI-powered agent that automatically reviews every Pull Request opened on a GitHub repository and posts structured feedback — bugs, security issues, performance problems, and improvement suggestions — directly as a comment on the PR. No human has to trigger it; it reacts to GitHub events in real time through webhooks.

## How It Works

```
New Pull Request opened on GitHub
            |
            v
   GitHub Webhook fires
            |
            v
   FastAPI server receives the event
            |
            v
   Agent fetches PR diff via GitHub API
            |
            v
   RAG layer searches the indexed codebase for related context
            |
            v
   LLM (Llama 3.3 70B via Groq) reviews the code
            |
            v
   Structured review is posted back to the PR as a comment
```

## Features

- **Fully autonomous** — triggers automatically on every new Pull Request via GitHub webhooks
- **Structured AI reviews** — bugs, security vulnerabilities, performance issues, code quality, and actionable suggestions
- **RAG-powered context** — indexes the target repository so the AI can cross-reference patterns across the codebase, not just the diff
- **Direct GitHub integration** — reads PRs and posts review comments using the GitHub REST API
- **Manual review mode** — review any PR on demand without waiting for a webhook event

## Tech Stack

| Layer | Technology |
|---|---|
| AI / LLM | Groq API (Llama 3.3 70B) |
| Agent orchestration | LangChain / LangGraph |
| Retrieval (RAG) | ChromaDB |
| GitHub integration | PyGithub (GitHub REST API) |
| Webhook server | FastAPI + Uvicorn |
| Tunneling (local dev) | ngrok |

## Project Structure

```
github-code-reviewer/
├── github_client.py      # Reads PR data and posts review comments via GitHub API
├── reviewer_agent.py     # Sends code to the LLM and gets a structured review back
├── rag_indexer.py        # Indexes the repo's codebase into ChromaDB for context search
├── webhook_server.py     # FastAPI server that listens for GitHub PR events
├── review_single_pr.py   # CLI tool to manually review any PR by number
├── auto_review.py        # Reviews a PR and posts the result without prompting
├── setup_webhook.py      # Registers the webhook on a GitHub repository
├── requirements.txt      # Python dependencies
└── .env.example          # Template for required environment variables
```

## Setup

### 1. Install dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables
Copy `.env.example` to `.env` and fill in your keys:
```
GROQ_API_KEY=your_groq_api_key_here
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_REPO=owner/repo-name
```

- **Groq API key** — free, from [console.groq.com](https://console.groq.com)
- **GitHub token** — classic Personal Access Token with `repo` scope, from GitHub Settings → Developer settings

### 3. Index your codebase (for RAG context)
```bash
python -c "from rag_indexer import index_repository; index_repository()"
```

### 4. Run a manual review on any PR
```bash
python review_single_pr.py <PR_NUMBER>
```

### 5. Run the autonomous webhook agent

Start the webhook server:
```bash
python webhook_server.py
```

Expose it to the internet (for local development) using ngrok:
```bash
ngrok http 8000
```

Register the webhook on your repository:
```bash
python setup_webhook.py
```

From this point on, every new Pull Request opened on the repository is automatically reviewed and commented on by the agent — no manual steps required.

## Example Output

```
## Code Review Summary
**Overall Assessment:** REQUEST CHANGES

## Bugs Found
- Function does not handle division by zero, which raises a ZeroDivisionError
- List access does not check for empty input, which raises an IndexError

## Security Issues
- Command injection vulnerability from concatenating user input into a shell command
- Hardcoded credentials found in the authentication function

## Suggestions
- Use parameterized queries instead of string concatenation
- Replace os.system calls with the subprocess module and proper input sanitization
- Add input validation and explicit error handling
```
