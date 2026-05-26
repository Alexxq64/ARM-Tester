from db.connection import DBConnection

class ProjectsRepo(DBConnection):
    def add_project(self, name, description="", root_path=""):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO projects (name, description, root_path) VALUES (?, ?, ?)",
                (name, description, root_path)
            )
            conn.commit()
            return cur.lastrowid
    
    def get_projects(self):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT project_id, name, description, root_path FROM projects")
            return cur.fetchall()
    
    def update_project(self, project_id, name, description, root_path):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE projects SET name = ?, description = ?, root_path = ? WHERE project_id = ?",
                (name, description, root_path, project_id)
            )
            conn.commit()
    
    def delete_project(self, project_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            conn.commit()