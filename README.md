# Autonomous GitHub Code Review Agent

An AI-assisted pull-request reviewer that reacts to GitHub webhook events,
retrieves the changed files and their patches, searches an indexed copy of the
repository for related context, asks an LLM for structured feedback, and posts
the result back to the pull request.

The project supports both autonomous webhook reviews and manual, human-approved
reviews from the command line.

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Review workflow](#review-workflow)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [GitHub permissions](#github-permissions)
- [Installation](#installation)
- [Configuration](#configuration)
- [Indexing the repository](#indexing-the-repository)
- [Manual review](#manual-review)
- [Autonomous webhook review](#autonomous-webhook-review)
- [Testing the automation](#testing-the-automation)
- [Review output](#review-output)
- [Limitations](#limitations)
- [Troubleshooting](#troubleshooting)
- [Security notes](#security-notes)

## Features

- **Automatic pull-request reviews:** listens for newly opened PRs through a
  GitHub webhook.
- **Structured feedback:** reports bugs, security concerns, performance
  issues, code-quality observations, and concrete suggestions.
- **Repository-aware context:** ChromaDB retrieves code related to the PR title
  and description.
- **GitHub integration:** PyGithub reads pull-request metadata and posts the
  generated review as a PR conversation comment.
- **Background processing:** FastAPI acknowledges the webhook quickly and runs
  the review as a background task.
- **Manual approval mode:** preview a generated review before deciding whether
  to publish it.
- **Direct automation mode:** review and post a selected PR without prompting.
- **Safe credential handling:** API keys and tokens are loaded from `.env`,
  which is excluded by `.gitignore`.

## Architecture

```text
GitHub pull request opened
          |
          v
+----------------------+
| GitHub webhook       |
| POST /webhook        |
+----------------------+
          |
          v
+----------------------+
| FastAPI background   |
| review task          |
+----------------------+
          |
          +-----------------------------+
          |                             |
          v                             v
+----------------------+      +----------------------+
| GitHub API           |      | ChromaDB index       |
| PR metadata + diffs  |      | related repo context |
+----------------------+      +----------------------+
          |                             |
          +--------------+--------------+
                         |
                         v
               +----------------------+
               | Groq LLM review      |
               | structured Markdown  |
               +----------------------+
                         |
                         v
               +----------------------+
               | GitHub PR comment    |
               +----------------------+
```

## Review workflow

1. GitHub sends a `pull_request` webhook event to `/webhook`.
2. The server checks that the action is `opened`.
3. A FastAPI background task starts processing the PR.
4. `github_client.py` retrieves the PR title, description, changed filenames,
   statuses, and available patches.
5. `rag_indexer.py` searches the local ChromaDB collection using the PR title
   and description.
6. `reviewer_agent.py` sends the PR data and retrieved context to
   `llama-3.3-70b-versatile` through Groq.
7. The generated Markdown review is posted as a pull-request comment.

## Project structure

```text
github-code-reviewer/
|-- github_client.py
|-- reviewer_agent.py
|-- rag_indexer.py
|-- webhook_server.py
|-- setup_webhook.py
|-- review_single_pr.py
|-- auto_review.py
|-- create_test_pr.py
|-- create_test_pr2.py
|-- requirements.txt
|-- .env.example
|-- .gitignore
`-- README.md
```

| File | Purpose |
|---|---|
| `github_client.py` | Creates the GitHub client, reads PR details, and posts review comments. |
| `reviewer_agent.py` | Builds the review prompt and calls the Groq chat-completions API. |
| `rag_indexer.py` | Downloads supported source files from the configured repository, stores them in ChromaDB, and performs semantic context searches. |
| `webhook_server.py` | Exposes the FastAPI webhook endpoint and runs review processing in the background. |
| `setup_webhook.py` | Registers a pull-request webhook for a public server or tunnel URL. |
| `review_single_pr.py` | Generates a review, prints it, and asks for confirmation before posting. |
| `auto_review.py` | Reviews PR number `1` and posts immediately; intended as a simple automation example. |
| `create_test_pr.py` | Creates a deliberately vulnerable test PR for demonstrating review behavior. |
| `create_test_pr2.py` | Creates a smaller test PR with common edge-case bugs. |

## Requirements

- Python 3.10 or newer
- A GitHub repository you can read and comment on
- A GitHub personal access token
- A Groq API key
- A public HTTPS URL for autonomous webhook mode

## GitHub permissions

Use a fine-grained personal access token whenever possible. Grant it access
only to the repository being reviewed.

Required repository permissions:

- **Contents: Read** - required to download source files for indexing.
- **Pull requests: Read and write** - required to read PRs and post comments.
- **Metadata: Read** - included for repository access.

The test-PR scripts also create branches, files, and pull requests. If you use
them, the token additionally needs:

- **Contents: Read and write**
- **Pull requests: Read and write**

Do not grant broader account or organization permissions unless they are
genuinely required.

## Installation

```bash
git clone https://github.com/iffat336/github-code-reviewer.git
cd github-code-reviewer

python -m venv venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

```bash
# macOS or Linux
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install groq
```

`reviewer_agent.py` uses the `groq` Python package. Install it explicitly as
shown above if the current `requirements.txt` does not yet provide it.

Create `.env`:

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

```bash
# macOS or Linux
cp .env.example .env
```

## Configuration

Edit `.env`:

```dotenv
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_token
GITHUB_REPO=owner/repository
```

| Variable | Required | Description |
|---|---:|---|
| `GROQ_API_KEY` | Yes | Authenticates requests to the Groq-hosted review model. |
| `GITHUB_TOKEN` | Yes | Authenticates repository, PR, comment, indexing, webhook, and optional test-PR operations. |
| `GITHUB_REPO` | Yes | Repository in `owner/repository` format. |

`.env`, `venv/`, `__pycache__/`, and `codebase_index/` are excluded from Git.

## Indexing the repository

The RAG layer must be populated before it can supply repository context:

```bash
python -c "from rag_indexer import index_repository; index_repository()"
```

The indexer:

1. traverses the configured GitHub repository;
2. reads supported source files;
3. stores up to the first 2,000 characters of each file;
4. saves vectors in the local `codebase_index/` directory.

Supported extensions:

```text
.py .js .ts .java .go .rb .php .cs
```

Run indexing again after substantial changes to the target repository.

## Manual review

Generate a review and choose whether to publish it:

```bash
python review_single_pr.py 5
```

Replace `5` with the pull-request number.

The script:

- fetches the PR;
- searches the indexed codebase;
- prints the generated review;
- asks `Post this review to GitHub? (yes/no)`;
- posts only when the answer is `yes`.

Manual mode is the safest starting point because a human can inspect the
output before it becomes visible to collaborators.

## Autonomous webhook review

### 1. Start the webhook server

```bash
python webhook_server.py
```

The server listens on:

```text
http://0.0.0.0:8000
```

Health check:

```bash
curl http://localhost:8000/
```

### 2. Expose the server

For local development, use a secure tunnel such as ngrok:

```bash
ngrok http 8000
```

Copy the public HTTPS URL.

### 3. Register the webhook

```bash
python setup_webhook.py https://your-public-url.example
```

The script registers:

```text
https://your-public-url.example/webhook
```

for GitHub `pull_request` events.

### 4. Open a pull request

When a PR is opened, GitHub sends the event, the server returns an immediate
success response, and the review runs as a background task.

## Testing the automation

Two helper scripts create demonstration PRs containing intentional defects:

```bash
python create_test_pr.py
python create_test_pr2.py
```

They create fixed branch names:

- `test-feature`
- `test-feature-2`

Delete existing branches with those names before rerunning the scripts, or
change the branch names in the scripts.

These helpers modify the configured GitHub repository. Use them only in a test
repository or when you deliberately want those demonstration pull requests.

`auto_review.py` is another demonstration script. It reviews PR number `1` and
posts without confirmation:

```bash
python auto_review.py
```

Change `pr_number` in the file before using it on a different PR.

## Review output

The prompt requests this structure:

```markdown
## Code Review Summary
**Overall Assessment:** APPROVE / REQUEST CHANGES / COMMENT

## Bugs Found
- ...

## Security Issues
- ...

## Performance Issues
- ...

## Code Quality
- ...

## Suggestions
- ...
```

Reviews are posted as normal PR conversation comments. They are not submitted
as GitHub's formal approve/request-changes review event.

## Limitations

- Webhook authenticity is not currently verified with a webhook secret.
- Only the `opened` pull-request action triggers an automatic review.
- Synchronize/reopen events do not trigger another review.
- The background task runs inside the web process and is not a durable queue.
- The code index stores only the first 2,000 characters of each source file.
- Only the listed programming-language extensions are indexed.
- GitHub may omit patches for very large or binary changes.
- The retrieval query uses only the PR title and description.
- Generated feedback may contain false positives or miss real defects.
- Reviews are comments rather than line-level annotations.

For production use, add webhook signature validation, idempotency, durable job
processing, retry handling, logging, observability, and repository-specific
review policies.

## Troubleshooting

### `Bad credentials` or HTTP 401

- Confirm `GITHUB_TOKEN` is current.
- Verify that the token can access `GITHUB_REPO`.
- Check the fine-grained repository permissions.
- Restart the Python process after editing `.env`.

### Repository not found

Set `GITHUB_REPO` exactly as:

```text
owner/repository
```

Private repositories require explicit token access.

### ChromaDB returns no useful context

- Run the indexer.
- Confirm the repository contains supported file types.
- Delete `codebase_index/` and rebuild when the schema or corpus changes.
- Use a descriptive PR title and body.

### Webhook is not firing

- Confirm the tunnel or server URL is still online.
- Check the repository's webhook delivery history in GitHub settings.
- Ensure the URL ends with `/webhook`.
- Confirm the content type is `application/json`.
- Verify the event is a newly opened pull request.

### Review is generated but not posted

- Check the token's pull-request write permission.
- Inspect the server console for the caught exception.
- Confirm the PR number belongs to the configured repository.

### Branch already exists in a test script

Delete the test branch in GitHub or update the hard-coded branch name before
running the helper again.

## Security notes

- Never place tokens directly in Python files.
- Never commit `.env`.
- Revoke any credential immediately if it appears in source control, logs,
  screenshots, chat, or terminal history.
- Add a GitHub webhook secret and verify `X-Hub-Signature-256` before trusting
  webhook payloads in a production deployment.
- Treat pull-request text and code as untrusted prompt input.
- Restrict token permissions and repository access to the minimum required.
- Review AI-generated feedback before acting on security-critical findings.

## License

No license file is currently included. Add one before redistribution or
external contribution.
