import time
import sqlite3 
import functools


query_cache = {}

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

def cache_query(func):
   
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # The 'query' argument is expected to be passed as a keyword argument
        # or as the second positional argument (after 'conn').
        # We need to find the query string.
        query = kwargs.get('query')
        if not query and len(args) > 1:
            # Assuming 'conn' is the first arg and 'query' is the second
            query = args[1]

        if not query:
            # If no query is found, execute the function without caching
            print("Warning: No 'query' argument found for caching. Executing directly.")
            return func(*args, **kwargs)

        # Check if the query result is already in the cache
        if query in query_cache:
            print(f"Cache hit for query: '{query}'")
            return query_cache[query]
        else:
            print(f"Cache miss for query: '{query}'. Executing query...")
            # If not in cache, execute the original function
            result = func(*args, **kwargs)
            # Store the result in the cache
            query_cache[query] = result
            print(f"Query result cached for: '{query}'")
            return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
for user in users_again:
    print(user)