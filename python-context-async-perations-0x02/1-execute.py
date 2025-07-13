import sqlite3
import os
from datetime import datetime

# Define the log file name (not directly used in this solution, but kept from original)
LOG_FILE_NAME = "query_log.txt"


# --- ExecuteQuery Context Manager ---
class ExecuteQuery:
    """
    A class-based context manager for executing a specific SQL query
    with optional parameters and automatically managing the database connection.
    """
    def __init__(self, db_name, query, params=None):
        """
        Initializes the ExecuteQuery with the database name, query, and parameters.

        Args:
            db_name (str): The name of the SQLite database file (e.g., 'users.db').
            query (str): The SQL query string to execute.
            params (tuple, list, or None): Parameters to bind to the query (e.g., (value1, value2)).
                                          Defaults to None for queries without parameters.
        """
        self.db_name = db_name
        self.query = query
        self.params = params if params is not None else () # Ensure params is an iterable
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        """
        Enters the runtime context.
        Opens the database connection, executes the query, and fetches results.

        Returns:
            list: The results fetched from the database query (list of tuples).
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Executing query: '{self.query}' with params: {self.params}")
            self.cursor.execute(self.query, self.params)
            self.results = self.cursor.fetchall()
            return self.results
        except sqlite3.Error as e:
            print(f"Error during query execution: {e}")
            # Re-raise the exception to indicate failure to the 'with' statement
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the runtime context.
        Closes the database connection and handles any exceptions.

        Args:
            exc_type (type): The type of the exception (if any).
            exc_val (Exception): The exception instance (if any).
            exc_tb (traceback): The traceback object (if any).
        """
        if self.conn:
            self.conn.close()
            print(f"Connection to {self.db_name} closed after query.")
        if exc_type:
            print(f"An exception occurred within the query block: {exc_type.__name__}: {exc_val}")
            # Returning False would propagate the exception, True would suppress it.
            return False # Propagate the exception
        return True # Indicate successful exit or handled exception

# --- Example Usage ---
if __name__ == "__main__":
    print("\n--- Using ExecuteQuery context manager ---")

    # Define the query and parameters
    query_string = "SELECT id, name, email, age FROM users WHERE age > ?"
    query_parameter = (25,) # Note the comma for a single-element tuple

    try:
        # Use the ExecuteQuery context manager
        with ExecuteQuery('users.db', query_string, query_parameter) as users_over_25:
            print("\nUsers older than 25:")
            if users_over_25:
                for user in users_over_25:
                    print(user)
            else:
                print("No users found older than 25.")

    except Exception as e:
        print(f"An error occurred in the main block: {e}")

