import sqlite3
from datetime import datetime

DB_PATH = "data/interview.db"


def init_reflection_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jd_keywords TEXT,
            question_quality INTEGER,
            evaluation_quality INTEGER,
            question_suggestions TEXT,
            evaluation_suggestions TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_reflection(reflection: dict, jd_keywords: list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reflections
        (jd_keywords, question_quality, evaluation_quality,
         question_suggestions, evaluation_suggestions, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        ",".join(jd_keywords),
        reflection.get("question_quality", 0),
        reflection.get("evaluation_quality", 0),
        "|".join(reflection.get("question_suggestions", [])),
        "|".join(reflection.get("evaluation_suggestions", [])),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))
    conn.commit()
    conn.close()


def get_recent_reflections(limit: int = 3) -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT question_quality, evaluation_quality,
               question_suggestions, evaluation_suggestions
        FROM reflections
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "question_quality": r[0],
            "evaluation_quality": r[1],
            "quest_suggestions": r[2].split("|") if r[2] else [],
            "evaluate_suggestions": r[3].split("|") if r[3] else [],
        }
        for r in rows
    ]