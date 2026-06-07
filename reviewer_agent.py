from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def review_code_with_claude(pr_details: dict, codebase_context: str = "") -> str:
    """Send the PR diff to Groq (Llama) and get a structured code review."""

    files_text = ""
    for f in pr_details["files"]:
        files_text += f"\n\n### File: {f['filename']} ({f['status']})\n```\n{f['patch']}\n```"

    prompt = f"""You are an expert code reviewer. Review this Pull Request and provide structured feedback.

PR Title: {pr_details['title']}
PR Description: {pr_details['description']}

Changed Files:{files_text}

{"Codebase Context:" + codebase_context if codebase_context else ""}

Provide your review in this exact format:

## Code Review Summary
**Overall Assessment:** [APPROVE / REQUEST CHANGES / COMMENT]

## Bugs Found
- List any bugs or logical errors (or "None found")

## Security Issues
- List any security vulnerabilities (or "None found")

## Performance Issues
- List any performance concerns (or "None found")

## Code Quality
- List style, readability, or maintainability issues

## Suggestions
- List specific improvement suggestions with examples if possible

Keep your review concise, specific, and actionable."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048
    )

    return response.choices[0].message.content
