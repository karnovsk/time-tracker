"""
Quick script to check database contents.
"""
import asyncio
from sqlalchemy import text
from app.database import engine


async def check_database():
    """Check what's in the database."""
    async with engine.connect() as conn:
        # Check users
        result = await conn.execute(text("SELECT id, email, created_at FROM users"))
        users = result.fetchall()

        print("\n=== USERS ===")
        if users:
            for user in users:
                print(f"ID: {user[0]}")
                print(f"Email: {user[1]}")
                print(f"Created: {user[2]}")
                print()
        else:
            print("No users found")

        # Check entries
        result = await conn.execute(text(
            "SELECT entry_date, casual_leisure_hours, serious_leisure_hours, "
            "project_leisure_hours, total_hours, casual_leisure_note "
            "FROM daily_entries ORDER BY entry_date DESC"
        ))
        entries = result.fetchall()

        print(f"\n=== DAILY ENTRIES ===")
        print(f"Total entries: {len(entries)}")
        if entries:
            print()
            for entry in entries:
                print(f"Date: {entry[0]}")
                print(f"Casual: {entry[1]}h - {entry[5]}")
                print(f"Serious: {entry[2]}h")
                print(f"Project: {entry[3]}h")
                print(f"Total: {entry[4]}h")
                print()


if __name__ == "__main__":
    asyncio.run(check_database())
