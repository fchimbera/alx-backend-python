import sqlite3
import os
from datetime import datetime

class DatabaseConnection:
    # A context manager for handling SQLite database connections
    def __init__(self, db_name):
        
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Successfully opened connection to {self.db_name}")
            return self.conn
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            # Re-raise the exception to indicate failure to the 'with' statement
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the runtime context related to this object.
        It closes the database connection and handles any exceptions that occurred
        within the 'with' block.

        Args:
            exc_type (type): The type of the exception (if any).
            exc_val (Exception): The exception instance (if any).
            exc_tb (traceback): The traceback object (if any).
        """
        if self.conn:
            self.conn.close()
            print(f"Connection to {self.db_name} closed.")
        if exc_type:
            print(f"An exception occurred: {exc_type.__name__}: {exc_val}")
            # Returning False would propagate the exception, True would suppress it.
            # We'll let it propagate for now to show errors.
            return False
        return True # Indicate that no exception occurred or it was handled

# --- Example Usage ---
if __name__ == "__main__":
    print("--- Using DatabaseConnection context manager ---")
    try:
        # Use the context manager to open and close the connection automatically
        with DatabaseConnection('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email FROM users")
            results = cursor.fetchall()

            print("\nQuery Results (SELECT * FROM users):")
            if results:
                for row in results:
                    print(row)
            else:
                print("No users found.")

    except Exception as e:
        print(f"An error occurred during query execution: {e}")

