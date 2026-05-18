from db.connection import DBConnection

class TestRunsRepo(DBConnection):
    def add_test_run(self, project_id, start_time, status):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO test_runs (project_id, start_time, status) VALUES (?, ?, ?)",
                (project_id, start_time, status)
            )
            conn.commit()
            return cur.lastrowid
    
    def update_test_run(self, run_id, end_time, status):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE test_runs SET end_time = ?, status = ? WHERE run_id = ?",
                (end_time, status, run_id)
            )
            conn.commit()
    
    def get_test_runs(self, project_id, date_from=None, date_to=None):
        with self._get_connection() as conn:
            cur = conn.cursor()
            query = "SELECT run_id, start_time, end_time, status FROM test_runs WHERE project_id = ?"
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
    
    def get_run_info(self, run_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT start_time, end_time, status FROM test_runs WHERE run_id = ?", (run_id,))
            row = cur.fetchone()
            if row:
                return {"start_time": row[0], "end_time": row[1], "status": row[2]}
            return None
    
    def delete_test_run(self, run_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM test_runs WHERE run_id = ?", (run_id,))
            conn.commit()