from db.connection import DBConnection

class TestCasesRepo(DBConnection):
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