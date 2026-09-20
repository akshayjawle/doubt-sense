import sqlite3

DB_NAME = "questions.db"

connection = sqlite3.connect(DB_NAME)

try:
    connection.execute(
        "ALTER TABLE questions ADD COLUMN answer TEXT"
    )

    print("answer column added.")

except sqlite3.OperationalError:
    print("answer column already exists.")

connection.commit()
connection.close()

print("Database upgrade completed.")