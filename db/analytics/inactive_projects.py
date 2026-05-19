# db/analytics/inactive_projects.py
from datetime import datetime, timedelta
from pathlib import Path
from db.database import Database

def get_projects_without_recent_runs(db, days_threshold=7):
    projects = db.get_projects()
    cutoff = (datetime.now() - timedelta(days=days_threshold)).strftime("%Y-%m-%d %H:%M:%S")
    inactive = []
    
    for proj_id, proj_name, _, root_path in projects:
        if not root_path:
            inactive.append((proj_id, proj_name))
            continue
        
        local_db = Path(root_path) / ".arm" / "arm_testing.db"
        if not local_db.exists():
            inactive.append((proj_id, proj_name))
            continue
        
        local = Database(str(local_db))
        runs = local.get_test_runs(1)
        if not runs or runs[0][1] < cutoff:
            inactive.append((proj_id, proj_name))
    
    return inactive