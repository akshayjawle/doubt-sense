import sqlite3


DB_NAME = "questions.db"


def get_connection():

    connection = sqlite3.connect(DB_NAME)

    connection.row_factory = sqlite3.Row

    return connection


def create_table():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS questions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            subject TEXT NOT NULL,

            question TEXT NOT NULL,

            cluster TEXT,

            status TEXT DEFAULT 'unanswered',

            priority TEXT DEFAULT 'low',

            votes INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    connection.close()
