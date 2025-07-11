import time
import sqlite3 
import functools

def with_db_connection(func):
   
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None  # Initialize conn to None
        try:
            # Establish a connection to the SQLite database
            conn = sqlite3.connect('users.db')
            
            result = func(conn, *args, **kwargs)
            return result
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")
            return None # Or re-raise the exception, depending on desired error handling
        finally:
            # Ensure the connection is closed, even if an error occurred
            if conn:
                conn.close()
                # print("Database connection closed.") # Uncomment for debugging
    return wrapper

def retry_on_failure(retries=3, delay=2):

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs): #
            attempts_left = retries
            while attempts_left >= 0:
                try:
                    print(f"Attempting '{func.__name__}' (Attempts left: {attempts_left + 1})")
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error in '{func.__name__}': {e}")
                    if attempts_left > 0:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                        attempts_left -= 1
                    else:
                        print(f"All {retries + 1} attempts failed for '{func.__name__}'. Re-raising last error.")
                        raise # Re-raise the last exception if no retries left
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)

