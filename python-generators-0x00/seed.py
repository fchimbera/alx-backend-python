#!/usr/bin/python3
import mysql.connector
import csv
import uuid

# Centralized connection config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Carly030224'
}
 
# Connect to MySQL Server
def connect_db():
    print("Attempting to connect to MySQL server...")
    try:
        # Connect without specifying a database first to create 'ALX_prodev'
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        if connection.is_connected():
            print("Successfully connected to MySQL Server.")
            return connection
        else:
            print("Connection failed, but no error raised.") # Should not happen
            return None
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL Server: {err}")
        return None

# Create ALX_prodev database
def create_database(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database 'ALX_prodev' created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
    finally:
        cursor.close()

# Connect to ALX_prodev specifically
def connect_to_prodev():
    print("Attempting to connect to 'ALX_prodev' database...")
    try:
        connection = mysql.connector.connect(**DB_CONFIG, database='ALX_prodev')
        if connection.is_connected():
            print("Successfully connected to 'ALX_prodev'.")
            return connection
        else:
            print("Connection to ALX_prodev failed, but no error raised.")
            return None
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev: {err}")
        return None

# Create table user_data
def create_table(connection):
    cursor = connection.cursor()
    create_query = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL NOT NULL,
        INDEX(user_id)
    )
    """
    try:
        cursor.execute(create_query)
        connection.commit() # Ensure commits are happening
        print("Table 'user_data' created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")
    finally:
        cursor.close()

# Insert data from CSV if not already in DB
def insert_data(connection, filename):
    cursor = connection.cursor()
    rows_inserted = 0
    try:
        with open(filename, newline='') as csvfile: # Use filename parameter
            reader = csv.DictReader(csvfile)
            for row in reader:
                cursor.execute("SELECT COUNT(*) FROM user_data WHERE email = %s", (row['email'],))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO user_data (user_id, name, email, age)
                        VALUES (%s, %s, %s, %s)
                    """, (str(uuid.uuid4()), row['name'], row['email'], row['age']))
                    rows_inserted += 1
        connection.commit() # Ensure commit after loop
        print(f"Data insertion complete. {rows_inserted} new rows inserted.")
    except FileNotFoundError:
        print(f"Error: CSV file '{filename}' not found.")
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
        connection.rollback() # Rollback on error
    finally:
        cursor.close()

# --- Main execution block ---
if __name__ == "__main__":
    # Ensure user_data.csv exists in the same directory as seed.py
    # or provide the full path to it.
    csv_file_name = 'user_data.csv' 
    
    # 1. Connect to the MySQL server (without specifying a DB yet)
    initial_connection = connect_db()
    if initial_connection:
        try:
            # 2. Create the database
            create_database(initial_connection)
        finally:
            initial_connection.close()
            print("Initial connection closed.")
    else:
        print("Could not establish initial connection to MySQL. Aborting.")
        exit(1)

    # 3. Now connect specifically to the newly created/existing database
    db_connection = connect_to_prodev()
    if db_connection:
        try:
            # 4. Create the table
            create_table(db_connection)
            # 5. Insert data
            insert_data(db_connection, csv_file_name)
        finally:
            db_connection.close()
            print("Database connection closed.")
    else:
        print("Could not connect to ALX_prodev database. Aborting.")
        exit(1)

    print("Script finished execution.")