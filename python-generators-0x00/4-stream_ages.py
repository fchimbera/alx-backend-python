#!/usr/bin/python3
from seed import connect_to_prodev

def stream_user_ages():
  
    connection = connect_to_prodev()
    if not connection:
        print("Error: Could not connect to the database to stream ages.")
        return # Exit if connection fails

    cursor = connection.cursor(dictionary=True)
    try:
        # Fetch all user data
        cursor.execute("SELECT age FROM user_data")

        # Loop 1: Iterate through each row and yield the age
        for row in cursor:
            yield row['age']
    except Exception as err:
        print(f"Error streaming user ages: {err}")
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def calculate_average_age():
   
    total_age = 0
    user_count = 0

    # Loop 2: Iterate through the ages yielded by the generator
    for age in stream_user_ages():
        total_age += age
        user_count += 1

    # Calculate the average age
    if user_count > 0:
        average_age = total_age / user_count
    else:
        average_age = 0.0 # Handle case with no users

    return average_age

if __name__ == "__main__":
    # Calculate the average age using the memory-efficient approach
    avg_age = calculate_average_age()

    # Print the result
    print(f"Average age of users: {avg_age:.2f}") # Format to two decimal places
