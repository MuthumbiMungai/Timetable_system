import sqlite3
import os

DB_NAME = "timetable.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(BASE_DIR, "schema.sql")

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        conn.commit()
        print("Database initialized successfully.")
    except FileNotFoundError:
        print(f"Error: schema.sql not found at {schema_path}")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()