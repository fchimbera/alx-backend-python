#!/usr/bin/python3
from seed import connect_to_prodev

def stream_users():
    """
    Generator that yields rows from the user_data table one by one
    """
    connection = connect_to_prodev()
    if not connection:
        return

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    for row in cursor:
        yield row

    cursor.close()
    connection.close()
