import sqlite3
from datetime import datetime

from .config import DB_FILE, NOTES_FILE


class Storage:
    def __init__(self, db_file=DB_FILE, notes_file=NOTES_FILE):
        self.db_file = str(db_file)
        self.notes_file = notes_file
        self.init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_text TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS custom_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phrase TEXT NOT NULL UNIQUE,
                    command_type TEXT NOT NULL,
                    value TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_text TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add_task(self, task_text):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO tasks (task_text) VALUES (?)",
                (task_text,),
            )

    def list_tasks(self):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT task_text FROM tasks ORDER BY id ASC"
            ).fetchall()
        return [row["task_text"] for row in rows]

    def clear_tasks(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks")

    def add_custom_command(self, phrase, command_type, value):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO custom_commands (phrase, command_type, value)
                VALUES (?, ?, ?)
                ON CONFLICT(phrase)
                DO UPDATE SET command_type = excluded.command_type,
                             value = excluded.value
                """,
                (phrase.lower(), command_type, value),
            )

    def get_custom_commands(self):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT phrase, command_type, value FROM custom_commands ORDER BY id ASC"
            ).fetchall()
        return [
            {"phrase": row["phrase"], "type": row["command_type"], "value": row["value"]}
            for row in rows
        ]

    def save_note(self, note_text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.notes_file.open("a", encoding="utf-8") as fh:
            fh.write(f"[{timestamp}] {note_text}\n")

    def get_note_history(self):
        if not self.notes_file.exists():
            return []
        with self.notes_file.open("r", encoding="utf-8") as fh:
            return [line.rstrip("\n") for line in fh.readlines()]
