from db.analytics.last_run import get_last_run_info
from db.analytics.failed_tests import get_failed_tests_last_run
from db.analytics.flaky_tests import get_flaky_tests
from db.analytics.slow_tests import get_slow_tests
from db.analytics.dynamic_stats import get_dynamic_stats
from db.analytics.inactive_projects import get_projects_without_recent_runs


class AnalyticsRepo:
    def __init__(self, db):
        self.db = db
    
    def get_last_run_info(self):
        return get_last_run_info(self.db)
    
    def get_failed_tests_last_run(self, limit=5):
        return get_failed_tests_last_run(self.db, limit)
    
    def get_flaky_tests(self, runs_count=5, change_threshold=2):
        return get_flaky_tests(self.db, runs_count, change_threshold)
    
    def get_slow_tests(self, threshold_sec=5.0, limit=5):
        return get_slow_tests(self.db, threshold_sec, limit)
    
    def get_dynamic_stats(self, runs_count=10):
        return get_dynamic_stats(self.db, runs_count)
    
    def get_projects_without_recent_runs(self, days_threshold=7):
        return get_projects_without_recent_runs(self.db, days_threshold)