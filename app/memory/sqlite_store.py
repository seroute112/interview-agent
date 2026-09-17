from posixpath import curdir
import sqlite3
import os
from datetime import datetime

DB_PATH = "data/interview.db"

def init_db():
    os.makedirs("data",exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            score TEXT,
            strengths TEXT,
            weaknesses TEXT,
            suggestion TEXT,
            weak_tags TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_evaluation(question,answer,score,strengths,weaknesses,suggestion,weak_tags):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO evaluations(question,answer,score,strengths,weaknesses,suggestion,weak_tags,created_at)
        VALUES(?,?,?,?,?,?,?,?)
    """,
        (question,answer,score,"|".join(strengths),"|".join(weaknesses),suggestion,"|".join(weak_tags),datetime.now().strftime("%Y-%m-%d %H:%M:%S")),    
    )
    conn.commit()
    conn.close()

def get_weak_points():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT weak_tags FROM evaluations")
    rows = cursor.fetchall()
    conn.close()

    tags = []
    for row in rows:
        if row[0]:
            tags.extend(row[0].split("|"))

    return tags

def get_evaluation_count():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM evaluations")
    count = cursor.fetchone()[0]
    conn.close()

    return count