from database import get_connection


connection = get_connection()


# Add votes column if it does not exist
try:
    connection.execute("""
        ALTER TABLE questions
        ADD COLUMN votes INTEGER DEFAULT 0
    """)
    print("votes column added.")
except Exception:
    print("votes column already exists.")


# Add created_at column if it does not exist
try:
    connection.execute("""
        ALTER TABLE questions
        ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """)
    print("created_at column added.")
except Exception:
    print("created_at column already exists.")


connection.commit()
connection.close()

print("Database upgrade completed.")