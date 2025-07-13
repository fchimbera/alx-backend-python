import sqlite3
import asyncio
import aiosqlite # Import the aiosqlite library
import os
from datetime import datetime

# Define the log file name (not directly used in this solution)
LOG_FILE_NAME = "query_log.txt"


# Define the database file path
DB_FILE = "users.db"

async def async_fetch_users():
    
    print("Starting async_fetch_users...")
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT id, name, email, age FROM users") as cursor:
            users = await cursor.fetchall()
            print("Finished async_fetch_users.")
            return users

async def async_fetch_older_users():
    
    print("Starting async_fetch_older_users...")
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT id, name, email, age FROM users WHERE age > ?", (30,)) as cursor:
            older_users = await cursor.fetchall()
            print("Finished async_fetch_older_users.")
            return older_users

async def fetch_concurrently():

    print("\n--- Starting concurrent fetch operations ---")
    try:
        # Use asyncio.gather to run both coroutines concurrently
        all_users, older_users = await asyncio.gather(
            async_fetch_users(),
            async_fetch_older_users()
        )

        print("\n--- Results from Concurrent Fetch ---")
        print("\nAll Users:")
        if all_users:
            for user in all_users:
                print(user)
        else:
            print("No users found.")

        print("\nUsers Older Than 30:")
        if older_users:
            for user in older_users:
                print(user)
        else:
            print("No users found older than 40.")

    except Exception as e:
        print(f"An error occurred during concurrent fetch: {e}")
    print("\n--- Concurrent fetch operations finished ---")


if __name__ == "__main__":
    print("Running asyncio.run(fetch_concurrently())...")
    # Run the main asynchronous function
    asyncio.run(fetch_concurrently())
    print("Script execution complete.")
