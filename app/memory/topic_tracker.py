import sqlite3
from datetime import datetime

DB_PATH = "data/interview.db"

def init_topic_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic_progress(
            topic TEXT PRIMARY KEY,
            total_attempts INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            consecutive_good INTEGER DEFAULT 0,
            mastery_level TEXT DEFAULT '未掌握',
            weight REAL DEFAULT 1.5,
            last_tested_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def update_topic_progress(topic:str,score:int,weak_tags:list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topic_progress WHERE topic = ?",(topic,))
    row = cursor.fetchone()

    if row is None:
        total_attempts = 0
        total_score = 0
        consecutive_good = 0
    else:
        total_attempts = row[1]
        total_score = row[2]
        consecutive_good = row[3]

    total_attempts += 1
    total_score += score
    avg = total_score / total_attempts

    if score >= 7:
        consecutive_good +=1
    else:
        consecutive_good = 0

    if consecutive_good >=3 and avg >=8:
        level,weight = "完全掌握",0.2
    elif consecutive_good >=2 and avg >=7:
        level,weight = "熟练",0.5 
    elif avg >=6:
        level,weight = "熟悉",1.0
    else:
        level,weight = "未掌握",1.5

    severe_tags = ["未作答","态度不端正","回答无效"]
    if any(tag in weak_tags for tag in severe_tags):
        level,weight = "未掌握",2.0
    cursor.execute(
        "INSERT OR REPLACE INTO topic_progress "
        "(topic, total_attempts, total_score, consecutive_good, mastery_level, weight, last_tested_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            topic,
            total_attempts,
            total_score,
            consecutive_good,
            level,
            weight,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    conn.commit()
    conn.close()

def get_topic_weights():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT topic,mastery_level,weight FROM topic_progress ORDER BY weight DESC ")

    rows = cursor.fetchall()

    conn.close()

    return [{"topic":r[0],"mastery_level":r[1],"weight":r[2]} for r in rows]

def get_weak_topics(threshold=1.0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT topic FROM topic_progress WHERE weight >= ? ORDER BY weight DESC",(threshold,))

    rows = cursor.fetchall()

    conn.close()

    return [r[0] for r in rows]