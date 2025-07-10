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

@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 
#### Fetch user by ID with automatic connection handling 

user = get_user_by_id(user_id=1)
print(user)