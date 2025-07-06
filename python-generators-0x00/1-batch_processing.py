#!/usr/bin/python3
from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    """
    Generator that yields batches of users from the user_data table
    """
    connection = connect_to_prodev()
    if not connection:
        return

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    batch = []
    for row in cursor:
        batch.append(row)
        if len(batch) == batch_size:
            yield batch
            batch = []

    if batch:
        yield batch  # yield any remaining users

    cursor.close()
    connection.close()

count = 0

def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25
    """
    global count
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user["age"] > 25:
                print(user)
                count += 1

if __name__ == "__main__":
    batch_size = 10  # Define the batch size
    batch_processing(batch_size)
    if count == 0:
        print("No users over the age of 25 found.")
    else:
        print(f"Total users over the age of 25: {count}")
    print("Batch processing completed.")    