#!/usr/bin/python3
from seed import connect_to_prodev

def paginate_users(page_size, offset):
    """
    Fetches a single page of user data from the database.

    Args:
        page_size (int): The maximum number of records to fetch per page.
        offset (int): The starting point (offset) for fetching records.

    Returns:
        list: A list of user dictionaries representing the fetched page.
              Returns an empty list if no connection or an error occurs.
    """
    connection = connect_to_prodev()
    if not connection:
        print("Error: Could not connect to the database for pagination.")
        return [] # Return an empty list if connection fails

    cursor = connection.cursor(dictionary=True)
    try:
        # SQL query to select a limited number of rows starting from an offset
        query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
        cursor.execute(query, (page_size, offset))
        page_data = cursor.fetchall() # Fetch all rows for the current page
        return page_data
    except Exception as err:
        print(f"Error fetching page from database: {err}")
        return []
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def lazy_paginate(page_size):
    """
    Generator function that lazily loads pages of user data from the database.
    It fetches the next page only when needed, starting at an offset of 0
    and incrementing the offset by page_size for subsequent fetches.

    Args:
        page_size (int): The number of users to include in each page.

    Yields:
        list: A list of user dictionaries representing a page of data.
              Yields an empty list if no more data is available.
    """
    offset = 0
    # to continuously fetch pages until no more data is returned
    while True:
        # Fetch the current page using the paginate_users helper function
        page = paginate_users(page_size, offset)

        # If the page is empty meaning no more users, break the loop
        if not page:
            break

        # Yield the current page of data
        yield page

        # Increment the offset for the next iteration to fetch the next page
        offset += page_size

if __name__ == "__main__":
    # --- Example Usage ---
    # Define the desired page size
    page_size = 3

    print(f"--- Starting lazy pagination with page size: {page_size} ---")

    # Iterate through the pages yielded by the lazy_paginate generator
    page_number = 1
    for page_data in lazy_paginate(page_size):
        print(f"\n--- Fetched Page {page_number} ---")
        if not page_data:
            print("No more users found.")
            break # Should be caught by the `if not page:` inside the generator, but good for clarity

        # Print each user in the current page
        for user in page_data:
            print(user)
        page_number += 1

    print("\n--- Lazy pagination completed ---")
