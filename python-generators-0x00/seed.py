import mysql.connector
import csv
import uuid

# Centralized connection config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Carly030224',
    'database': ''
}
 
# Connect to MySQL Server
def connect_db():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Create ALX_prodev database
def create_database(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    cursor.close()

# Connect to ALX_prodev specifically
def connect_to_prodev():
    try:
        connection = mysql.connector.connect(**DB_CONFIG, database='ALX_prodev')
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
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
    cursor.execute(create_query)
    connection.commit()
    cursor.close()

# Insert data from CSV if not already in DB
def insert_data(connection, filename):
    cursor = connection.cursor()
    with open('user_data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute("SELECT COUNT(*) FROM user_data WHERE email = %s", (row['email'],))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                """, (str(uuid.uuid4()), row['name'], row['email'], row['age']))
    connection.commit()
    cursor.close()
