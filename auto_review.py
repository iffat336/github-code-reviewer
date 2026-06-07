from github_client import get_pr_details, post_review_comment
from reviewer_agent import review_code_with_claude
from rag_indexer import search_codebase

pr_number = 1
print(f"Reviewing PR #{pr_number}...")

pr_details = get_pr_details(pr_number)
print(f"Title: {pr_details['title']}")
print(f"Files changed: {len(pr_details['files'])}")

query = f"{pr_details['title']} {pr_details['description']}"
context = search_codebase(query)

print("\nAsking AI to review the code...")
review = review_code_with_claude(pr_details, context)

print("\n" + "="*60)
print(review)
print("="*60)

post_review_comment(pr_number, review)
print("\nReview posted to GitHub successfully!")
