# db/database.py
from db.connection import DBConnection
from db.projects_repo import ProjectsRepo
from db.test_cases_repo import TestCasesRepo
from db.test_runs_repo import TestRunsRepo
from db.test_results_repo import TestResultsRepo
from db.reports_repo import ReportsRepo
from db.users_repo import UsersRepo

class Database(ProjectsRepo, TestCasesRepo, TestRunsRepo, TestResultsRepo, ReportsRepo, UsersRepo):
    def __init__(self, db_path="arm_testing.db", include_projects=True):
        self.db_path = db_path
        self.include_projects = include_projects
        self._init_tables()
    
    def _init_tables(self):
        conn_holder = DBConnection(self.db_path)
        conn_holder.init_tables(include_projects=self.include_projects)