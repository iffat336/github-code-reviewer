import os
import json

def get_user_password(username):
    # BUG: command injection - never use os.system with user input
    result = os.system('cat /etc/passwd | grep ' + username)
    return result

def calculate_average(numbers):
    total = 0
    for n in numbers:
        total = total + n
    # BUG: crashes with ZeroDivisionError if list is empty
    average = total / len(numbers)
    return average

def save_user_data(user_id, data):
    # BUG: SQL injection - never concat user input into queries
    query = 'SELECT * FROM users WHERE id = ' + user_id
    # BUG: file handle never closed - resource leak
    file = open('users.json', 'w')
    json.dump(data, file)

def login(username, password):
    # BUG: hardcoded credentials
    if username == 'admin' and password == 'admin123':
        return True
    return False