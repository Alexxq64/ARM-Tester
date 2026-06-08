# db/users_repo.py
from db.connection import DBConnection

class UsersRepo(DBConnection):
    def get_user(self, username, password):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, username FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
            return cur.fetchone()