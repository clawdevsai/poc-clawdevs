import sqlite3
import os
import time

DB_PATH = os.environ.get("KANBAN_DB_PATH", "/tmp/kanban.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Table for Tasks, Stories, Epics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issues (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL, -- task, story, epic
        title TEXT NOT NULL,
        summary TEXT,
        state TEXT NOT NULL,
        priority TEXT DEFAULT 'medium',
        created_by TEXT,
        created_at INTEGER,
        updated_at INTEGER
    )
    """)
    
    # Table for Agent Activities
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp INTEGER
    )
    """)
    
    conn.commit()
    conn.close()

def save_issue(issue_id, issue_type, title, summary, state, priority, agent):
    conn = get_db()
    now = int(time.time() * 1000)
    conn.execute("""
    INSERT INTO issues (id, type, title, summary, state, priority, created_by, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        type=excluded.type,
        title=excluded.title,
        summary=excluded.summary,
        state=excluded.state,
        priority=excluded.priority,
        updated_at=excluded.updated_at
    """, (issue_id, issue_type, title, summary, state, priority, agent, now, now))
    conn.commit()
    conn.close()

def update_issue_state(issue_id, state):
    conn = get_db()
    now = int(time.time() * 1000)
    conn.execute("UPDATE issues SET state = ?, updated_at = ? WHERE id = ?", (state, now, issue_id))
    conn.commit()
    conn.close()

def add_activity(agent, message):
    conn = get_db()
    conn.execute("INSERT INTO activities (agent, message, timestamp) VALUES (?, ?, ?)",
                 (agent, message, int(time.time() * 1000)))
    conn.commit()
    conn.close()

def get_all_issues():
    conn = get_db()
    rows = conn.execute("SELECT * FROM issues ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_activities(limit=50):
    conn = get_db()
    rows = conn.execute("SELECT * FROM activities ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
