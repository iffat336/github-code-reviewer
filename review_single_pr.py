"""
Run this to manually review a single PR without needing a webhook.
Usage: python review_single_pr.py 5
(replace 5 with your PR number)
"""
import sys
from github_client import get_pr_details, post_review_comment
from reviewer_agent import review_code_with_claude
from rag_indexer import search_codebase

def main():
    if len(sys.argv) < 2:
        print("Usage: python review_single_pr.py <PR_NUMBER>")
        print("Example: python review_single_pr.py 5")
        return

    pr_number = int(sys.argv[1])
    print(f"Reviewing PR #{pr_number}...")

    # Get PR details from GitHub
    pr_details = get_pr_details(pr_number)
    print(f"Title: {pr_details['title']}")
    print(f"Files changed: {len(pr_details['files'])}")

    # Search codebase for context
    query = f"{pr_details['title']} {pr_details['description']}"
    context = search_codebase(query)

    # Get Claude's review
    print("\nAsking Claude to review...")
    review = review_code_with_claude(pr_details, context)

    print("\n" + "="*60)
    print("CLAUDE'S REVIEW:")
    print("="*60)
    print(review)

    # Ask if you want to post it
    answer = input("\nPost this review to GitHub? (yes/no): ")
    if answer.lower() == "yes":
        post_review_comment(pr_number, review)
        print("Review posted successfully!")

if __name__ == "__main__":
    main()
