from db.connection import DBConnection

class TestResultsRepo(DBConnection):
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