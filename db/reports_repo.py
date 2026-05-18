from db.connection import DBConnection

class ReportsRepo(DBConnection):
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