"""测试侧数据库探针，只通过 SELECT 核对结果。"""
import sqlite3


class DatabaseProbe:
    def __init__(self, path):
        self.path = path

    def task(self, task_id):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            return dict(row) if row else None
        finally:
            connection.close()

    def task_count(self):
        connection = sqlite3.connect(self.path)
        try:
            return connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        finally:
            connection.close()
