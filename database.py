"""SQLite data access layer for the Task Manager API."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "tasks.db"


def get_connection():
    """Return a new SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the tasks table if it does not already exist."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'completed')),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def row_to_dict(row):
    """Convert a sqlite3.Row into a plain dict."""
    if row is None:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "created_at": row["created_at"],
    }


def create_task(title, description, status):
    """Insert a new task and return the full row as a dict."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
            (title, description, status),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def get_all_tasks():
    """Return all tasks ordered by id ascending."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM tasks ORDER BY id ASC"
        ).fetchall()
        return [row_to_dict(row) for row in rows]
    finally:
        conn.close()


def get_task_by_id(task_id):
    """Return a single task by id, or None if not found."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def update_task(task_id, fields):
    """
    Update a task with the given fields (partial update).

    fields may contain: title, description, status.
    Only keys present in fields are updated.
    Returns the updated task dict, or None if the task does not exist.
    """
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if existing is None:
            return None

        new_title = fields.get("title", existing["title"])
        new_description = fields.get("description", existing["description"])
        new_status = fields.get("status", existing["status"])

        conn.execute(
            "UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?",
            (new_title, new_description, new_status, task_id),
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def delete_task(task_id):
    """Delete a task by id. Returns True if deleted, False if not found."""
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
