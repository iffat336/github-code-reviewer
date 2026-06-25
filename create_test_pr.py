import os

from dotenv import load_dotenv
from github import Github, Auth

load_dotenv()
TOKEN = os.environ["GITHUB_TOKEN"]
g = Github(auth=Auth.Token(TOKEN))
repo = g.get_repo('iffat336/github-code-reviewer')

# Create feature branch from main
main = repo.get_branch('main')
repo.create_git_ref(ref='refs/heads/test-feature', sha=main.commit.sha)
print('Branch created: test-feature')

# Buggy Python file with real issues for AI to catch
buggy_code = "\n".join([
    "import os",
    "import json",
    "",
    "def get_user_password(username):",
    "    # BUG: command injection - never use os.system with user input",
    "    result = os.system('cat /etc/passwd | grep ' + username)",
    "    return result",
    "",
    "def calculate_average(numbers):",
    "    total = 0",
    "    for n in numbers:",
    "        total = total + n",
    "    # BUG: crashes with ZeroDivisionError if list is empty",
    "    average = total / len(numbers)",
    "    return average",
    "",
    "def save_user_data(user_id, data):",
    "    # BUG: SQL injection - never concat user input into queries",
    "    query = 'SELECT * FROM users WHERE id = ' + user_id",
    "    # BUG: file handle never closed - resource leak",
    "    file = open('users.json', 'w')",
    "    json.dump(data, file)",
    "",
    "def login(username, password):",
    "    # BUG: hardcoded credentials",
    "    if username == 'admin' and password == 'admin123':",
    "        return True",
    "    return False",
])

# Push buggy file to feature branch
repo.create_file(
    path='user_manager.py',
    message='Add user manager module',
    content=buggy_code,
    branch='test-feature'
)
print('File pushed: user_manager.py')

# Open Pull Request
pr = repo.create_pull(
    title='Add user manager module',
    body='Adds user management: login, password retrieval, data saving, and average calculation.',
    head='test-feature',
    base='main'
)
print(f'PR opened: #{pr.number} — {pr.title}')
print(f'URL: {pr.html_url}')
