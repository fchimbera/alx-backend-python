import sqlite3
import functools
import os
from datetime import datetime

LOG_FILE_NAME = "query_log.txt"
#### decorator to log SQL queries
def log_queries(func):
    """
    A decorator that logs the SQL query executed by the decorated function
    to a text file named 'query_log.txt' in the same directory.
    Assumes the decorated function takes 'query' as one of its arguments.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Determine the path to the log file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(script_dir, LOG_FILE_NAME)

        # Extract the query from arguments
        query = kwargs.get('query')
        if not query and args:
            # Assuming 'query' is the first positional argument if not in kwargs
            # This might need adjustment if 'query' is not always the first arg
            query = args[0]

        # Log the query to the file
        if query:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] Executing SQL Query: {query}\n"
            try:
                with open(log_file_path, 'a') as f:
                    f.write(log_message)
                print(f"Logged query to {LOG_FILE_NAME}: {query}") # Also print to console for immediate feedback
            except IOError as e:
                print(f"Error writing to log file {LOG_FILE_NAME}: {e}")
        else:
            print("No SQL query found in function arguments to log.")

        return func(*args, **kwargs)
    return wrapper
@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
# Note: For this code to run without error, a 'users.db' file with a 'users' table
# must exist in the same directory, or you'll get an operational error.
# For demonstration purposes, you would typically add a setup_database() function.
# However, as per your instruction, only the decorator code is provided.
users = fetch_all_users(query="SELECT * FROM users")
for user in users:
    print(user)