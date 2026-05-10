from pathlib import Path
import sqlite3

class Database:
    def __init__(self, db_path="arm_testing.db"):
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_tables(self):
        with self._get_connection() as conn:
            cur = conn.cursor()
            # Проекты
            cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT
                )
            """)
            # Тестовые сценарии
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_cases (
                    test_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    group_name TEXT,
                    test_path TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
                )
            """)
            # Запуски
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
                )
            """)
            # Результаты тестов — расширенная таблица
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    test_id INTEGER,
                    test_function_name TEXT,
                    test_file_path TEXT,
                    status TEXT NOT NULL,
                    execution_time REAL,
                    error_message TEXT,
                    FOREIGN KEY (run_id) REFERENCES test_runs (run_id) ON DELETE CASCADE,
                    FOREIGN KEY (test_id) REFERENCES test_cases (test_id) ON DELETE CASCADE
                )
            """)
            # Артефакты
            cur.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    result_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    artifact_type TEXT,
                    FOREIGN KEY (result_id) REFERENCES test_results (result_id) ON DELETE CASCADE
                )
            """)
            # Отчеты
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES test_runs (run_id) ON DELETE CASCADE
                )
            """)
            
            # Добавляем новые колонки в test_results, если таблица уже существовала
            cur.execute("PRAGMA table_info(test_results)")
            columns = [col[1] for col in cur.fetchall()]
            if "test_function_name" not in columns:
                cur.execute("ALTER TABLE test_results ADD COLUMN test_function_name TEXT")
            if "test_file_path" not in columns:
                cur.execute("ALTER TABLE test_results ADD COLUMN test_file_path TEXT")
            
            conn.commit()

    def add_project(self, name, description=""):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO projects (name, description) VALUES (?, ?)",
                (name, description)
            )
            conn.commit()
            return cur.lastrowid

    def get_projects(self):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT project_id, name, description FROM projects")
            return cur.fetchall()

    def add_test_case(self, project_id, name, test_path, group_name="", is_active=1):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO test_cases (project_id, name, group_name, test_path, is_active) VALUES (?, ?, ?, ?, ?)",
                (project_id, name, group_name, test_path, is_active)
            )
            conn.commit()
            return cur.lastrowid

    def get_test_cases(self, project_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT test_id, name, group_name, test_path, is_active FROM test_cases WHERE project_id = ?",
                (project_id,)
            )
            return cur.fetchall()

    def update_test_case(self, test_id, name, group_name, test_path, is_active):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE test_cases SET name = ?, group_name = ?, test_path = ?, is_active = ? WHERE test_id = ?",
                (name, group_name, test_path, is_active, test_id)
            )
            conn.commit()

    def delete_test_case(self, test_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM test_cases WHERE test_id = ?", (test_id,))
            conn.commit()   

    def add_test_run(self, project_id, start_time, status):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO test_runs (project_id, start_time, status) VALUES (?, ?, ?)",
                (project_id, start_time, status)
            )
            conn.commit()
            return cur.lastrowid

    def add_test_result(self, run_id, test_id, test_function_name, test_file_path, status, execution_time, error_message):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO test_results 
                   (run_id, test_id, test_function_name, test_file_path, status, execution_time, error_message) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (run_id, test_id, test_function_name, test_file_path, status, execution_time, error_message)
            )
            conn.commit()

    def update_test_run(self, run_id, end_time, status):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE test_runs SET end_time = ?, status = ? WHERE run_id = ?",
                (end_time, status, run_id)
            )
            conn.commit() 

    def get_test_case_by_id(self, test_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT test_id, name, group_name, test_path, is_active FROM test_cases WHERE test_id = ?",
                (test_id,)
            )
            row = cur.fetchone()
            if row:
                return {
                    "test_id": row[0],
                    "name": row[1],
                    "group_name": row[2],
                    "test_path": row[3],
                    "is_active": row[4]
                }
            return None

    def get_test_results_by_run(self, run_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT test_function_name, test_file_path, status, error_message
                FROM test_results
                WHERE run_id = ?
                ORDER BY result_id
            """, (run_id,))
            return cur.fetchall()

    def get_test_runs(self, project_id, date_from=None, date_to=None):
        with self._get_connection() as conn:
            cur = conn.cursor()
            query = """
                SELECT run_id, start_time, end_time, status
                FROM test_runs
                WHERE project_id = ?
            """
            params = [project_id]
            
            if date_from:
                query += " AND start_time >= ?"
                params.append(date_from)
            if date_to:
                query += " AND start_time <= ?"
                params.append(date_to)
            
            query += " ORDER BY run_id DESC"
            
            cur.execute(query, params)
            return cur.fetchall()

    def delete_test_run(self, run_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM test_runs WHERE run_id = ?", (run_id,))
            conn.commit()

    def get_run_info(self, run_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT start_time, end_time, status FROM test_runs WHERE run_id = ?", (run_id,))
            row = cur.fetchone()
            if row:
                return {"start_time": row[0], "end_time": row[1], "status": row[2]}
            return None

    def add_report(self, run_id, file_path, created_at):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO reports (run_id, file_path, created_at) VALUES (?, ?, ?)",
                (run_id, file_path, created_at)
            )
            conn.commit()
            return cur.lastrowid

    def get_reports_by_run(self, run_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT report_id, file_path, created_at
                FROM reports
                WHERE run_id = ?
                ORDER BY created_at DESC
            """, (run_id,))
            return cur.fetchall()

    def delete_report(self, report_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM reports WHERE report_id = ?", (report_id,))
            conn.commit()