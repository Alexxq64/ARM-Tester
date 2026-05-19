from pathlib import Path
from db.database import Database


class TableModel:
    def __init__(self, db):
        self.db = db
    
    def load(self, filters):
        projects = self.db.get_projects()
        data = []
        
        for proj_id, proj_name, _, root_path in projects:
            # Фильтр по проекту
            if filters.get("project") and filters["project"] != "Все проекты":
                if filters["project"] != proj_name:
                    continue
            
            # Определяем, какую БД использовать для тестов
            if root_path:
                local_db_path = Path(root_path) / ".arm" / "arm_testing.db"
                if not local_db_path.exists():
                    continue
                tests_db = Database(str(local_db_path))
                local_project_id = 1
            else:
                tests_db = self.db
                local_project_id = proj_id
            
            tests = tests_db.get_test_cases(local_project_id)
            
            for test in tests:
                test_id, test_name, group, test_path, is_active = test
                
                # Фильтр по группе
                if filters.get("group") and filters["group"] != "Все группы":
                    if group != filters["group"]:
                        continue
                
                # Получаем последний статус
                last_status = None
                last_error = None
                last_run_time = None
                
                runs = tests_db.get_test_runs(local_project_id)
                for run_id, start_time, end_time, status in runs:
                    if status == "running":
                        continue
                    results = tests_db.get_test_results_by_run(run_id)
                    for r in results:
                        r_test_name = r[0] if r[0] else ""
                        r_test_path = r[1] if r[1] else ""
                        if (test_name and test_name in r_test_name) or (test_path and test_path in r_test_path):
                            last_status = r[2]
                            last_error = r[3] if r[3] else ""
                            last_run_time = start_time[:19] if start_time else ""
                            break
                    if last_status:
                        break
                
                # Фильтр по статусу
                if filters.get("status") and filters["status"] != "Все":
                    if last_status != filters["status"]:
                        continue
                
                data.append({
                    "project_name": proj_name,
                    "test_name": test_name or "",
                    "group": group or "",
                    "last_run": last_run_time or "",
                    "status": last_status or "",
                    "error": (last_error or "")[:100],
                    "project_id": proj_id,
                    "test_id": test_id,
                    "root_path": root_path or "",
                    "test_path": test_path or "",
                })
        
        # Фильтр по поиску (название теста)
        search = filters.get("search", "").lower()
        if search:
            data = [item for item in data if search in item.get("test_name", "").lower()]
        
        return data