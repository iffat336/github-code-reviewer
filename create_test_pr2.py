import os

from dotenv import load_dotenv
from github import Github, Auth

load_dotenv()
TOKEN = os.environ["GITHUB_TOKEN"]
g = Github(auth=Auth.Token(TOKEN))
repo = g.get_repo('iffat336/github-code-reviewer')

main = repo.get_branch('main')
repo.create_git_ref(ref='refs/heads/test-feature-2', sha=main.commit.sha)
print('Branch created: test-feature-2')

code = "\n".join([
    "def divide_numbers(a, b):",
    "    return a / b",
    "",
    "def get_first_item(items):",
    "    return items[0]",
    "",
    "def merge_dicts(dict1, dict2):",
    "    dict1.update(dict2)",
    "    return dict1",
])

repo.create_file(
    path='math_utils.py',
    message='Add math utility functions',
    content=code,
    branch='test-feature-2'
)
print('File pushed: math_utils.py')

pr = repo.create_pull(
    title='Add math utility functions',
    body='Adds helper functions for division, list access, and dict merging.',
    head='test-feature-2',
    base='main'
)
print(f'PR opened: #{pr.number}')
print(f'URL: {pr.html_url}')
print('\nWatch — the webhook should trigger the AI review automatically now!')
