#!/usr/bin/python3
from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    """
    Generator that yields batches of users from the user_data table
    """
    print(f"--- Entering stream_users_in_batches with batch_size: {batch_size} ---")
    
    connection = connect_to_prodev()
    if not connection:
        print("Failed to connect to the database in stream_users_in_batches. Exiting generator.")
        return
    else:
        print("Connected to the database successfully in stream_users_in_batches.")

    cursor = connection.cursor(dictionary=True)
    print("Executing SELECT * FROM user_data...")
    cursor.execute("SELECT * FROM user_data")
    print("SELECT query executed. Starting to fetch rows.")

    batch = []
    row_count = 0
    for row in cursor:
        row_count += 1
        batch.append(row)
        print(f"  Added user to batch. Current batch size: {len(batch)}")
        if len(batch) == batch_size:
            print(f"  Batch full (size {batch_size}). Yielding batch.")
            yield batch
            batch = [] # Reset batch after yielding
            print("  Batch reset.")

    if batch:
        print(f"  End of data. Yielding remaining batch (size: {len(batch)}).")
        yield batch  # yield any remaining users
    else:
        print("  No remaining users to yield in the last batch.")

    print("Closing cursor and connection in stream_users_in_batches.")
    cursor.close()
    connection.close()
    print(f"--- Exiting stream_users_in_batches. Total rows processed: {row_count} ---")


def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25
    """
    print(f"\n--- Entering batch_processing with batch_size: {batch_size} ---")
    processed_count = 0
    filtered_count = 0

    for batch_num, batch in enumerate(stream_users_in_batches(batch_size)):
        print(f"  Received batch number {batch_num + 1} (size: {len(batch)}) in batch_processing.")
        for user in batch:
            processed_count += 1
            print(f"    Checking user: {user['name']} (Age: {user['age']})")
            if user["age"] > 25:
                filtered_count += 1
                print(f"      User {user['name']} (Age: {user['age']}) is OVER 25. Printing:")
                print(user)
            else:
                print(f"      User {user['name']} (Age: {user['age']}) is NOT over 25. Skipping.")
    
    print(f"\n--- Exiting batch_processing. Total users checked: {processed_count}, Total users printed: {filtered_count} ---")

# Example usage (you'll need to call batch_processing from another script or add it here)
if __name__ == "__main__":
    print("--- Starting main execution of 1-batch_processing.py ---")
    batch_processing(2) # Example: process in batches of 2
    # You might want to try different batch sizes like 1, 5, or 10
    print("--- Script 1-batch_processing.py finished ---")