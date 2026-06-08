# db/connection.py
import sqlite3
from pathlib import Path


class DBConnection:
    def __init__(self, db_path="arm_testing.db"):
        self.db_path = db_path
    
    def _get_connection(self):
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def init_tables(self, include_projects=True):
        with self._get_connection() as conn:
            cur = conn.cursor()
            
            # Всегда создаём таблицу projects (для FOREIGN KEY)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    root_path TEXT
                )
            """)
            
            # Добавляем колонку root_path, если её нет (только для глобальной БД)
            if include_projects:
                cur.execute("PRAGMA table_info(projects)")
                columns = [col[1] for col in cur.fetchall()]
                if "root_path" not in columns:
                    cur.execute("ALTER TABLE projects ADD COLUMN root_path TEXT")
            
            # Для локальной БД вставляем запись с project_id=1
            if not include_projects:
                cur.execute("INSERT OR IGNORE INTO projects (project_id, name, description, root_path) VALUES (1, 'local_project', '', '')")
            
            # Только для глобальной БД создаём таблицу users и добавляем тестового пользователя
            if include_projects:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL
                    )
                """)
                cur.execute("SELECT COUNT(*) FROM users")
                if cur.fetchone()[0] == 0:
                    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("tester", "12345"))
            
            # Тестовые сценарии
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_cases (
                    test_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    group_name TEXT,
                    test_path TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    test_params TEXT DEFAULT '{}',
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
            
            # Результаты
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
            
            cur.execute("PRAGMA table_info(test_results)")
            columns = [col[1] for col in cur.fetchall()]
            if "test_function_name" not in columns:
                cur.execute("ALTER TABLE test_results ADD COLUMN test_function_name TEXT")
            if "test_file_path" not in columns:
                cur.execute("ALTER TABLE test_results ADD COLUMN test_file_path TEXT")
            
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
            
            # Отчёты
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES test_runs (run_id) ON DELETE CASCADE
                )
            """)
            
            # Добавляем колонку test_params для существующих БД
            cur.execute("PRAGMA table_info(test_cases)")
            columns = [col[1] for col in cur.fetchall()]
            if "test_params" not in columns:
                cur.execute("ALTER TABLE test_cases ADD COLUMN test_params TEXT DEFAULT '{}'")
            
            conn.commit()