import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = "timetable.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    schema_path = Path("database/schema.sql")
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    conn.close()
    print("✅ Database initialized.")

def sync_from_google_sheets():
    try:
        courses_url = "https://docs.google.com/spreadsheets/d/1JeFCSLiwSbFeDoVmufiq9VAdkswQVh2Cuq2GXDioWFk/export?format=csv"
        trainers_url = "https://docs.google.com/spreadsheets/d/1huV6DeH4MLBXHNboJ-LYCQNVmpmhncPCxgIWanCyvbI/export?format=csv"

        courses_df = pd.read_csv(courses_url)
        trainers_df = pd.read_csv(trainers_url)

        conn = get_connection()
        cur = conn.cursor()

        # Clear previous data for fresh sync
        cur.execute("DELETE FROM intakes")
        cur.execute("DELETE FROM courses")
        cur.execute("DELETE FROM departments")
        cur.execute("DELETE FROM trainers")

        current_dept = None
        current_course_id = None

        # Parse Courses & Intakes Sheet
        for _, row in courses_df.iterrows():
            col0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            col1 = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
            col2 = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""

            if col0 and not col1 and len(col0) > 10 and "COURSE" not in col0.upper():
                current_dept = col0
                cur.execute("INSERT OR IGNORE INTO departments (name, code) VALUES (?, ?)", 
                           (current_dept, current_dept[:10].upper()))
                conn.commit()

            elif ("DIPLOMA" in col0.upper() or "CERTIFICATE" in col0.upper() or "KENYA REGISTERED" in col0.upper()) and current_dept:
                course_name = col0
                course_code = col1 if col1 else col0.split()[-1] if " " in col0 else col0[:10]
                cur.execute("SELECT id FROM departments WHERE name=?", (current_dept,))
                dept = cur.fetchone()
                if dept:
                    cur.execute("INSERT OR IGNORE INTO courses (department_id, name, code) VALUES (?, ?, ?)",
                               (dept['id'], course_name, course_code))
                    conn.commit()
                    cur.execute("SELECT id FROM courses WHERE name=?", (course_name,))
                    course = cur.fetchone()
                    current_course_id = course['id'] if course else None

            elif col2 and col2 not in ["INTAKES", "", "nan"] and current_course_id:
                cur.execute("INSERT OR IGNORE INTO intakes (course_id, label, academic_year) VALUES (?, ?, '2025/2026')",
                           (current_course_id, col2))

        # Parse Trainers Sheet
        for _, row in trainers_df.iterrows():
            if len(row) < 2:
                continue
            dept_part = str(row.iloc[0]).strip()
            trainer_name = str(row.iloc[1]).strip()
            if trainer_name and trainer_name.lower() != "nan" and len(trainer_name) > 3:
                cur.execute("SELECT id FROM departments WHERE name LIKE ?", (f"%{dept_part}%",))
                dept = cur.fetchone()
                if dept:
                    cur.execute("INSERT OR IGNORE INTO trainers (department_id, full_name) VALUES (?, ?)",
                               (dept['id'], trainer_name))

        conn.commit()
        conn.close()
        print("✅ Successfully synced from Google Sheets!")
        return True

    except Exception as e:
        print(f"❌ Sync failed: {str(e)}")
        return False