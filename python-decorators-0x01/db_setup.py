import sqlite3
import functools
import os
from datetime import datetime

# Define the log file name
LOG_FILE_NAME = "query_log.txt"

# Create a dummy database and table for demonstration purposes
def setup_database():
    """
    Sets up a simple SQLite database 'users.db' with a 'users' table.
    Inserts dummy data if the table is empty.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    # Insert some dummy data if the table is empty
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
    conn.commit()
    conn.close()

# Call the setup function to ensure the database exists
setup_database()
