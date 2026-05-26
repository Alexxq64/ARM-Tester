# gui/main_window.py
import sys
import os

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from gui.filters_bar import FiltersBar
from gui.table_view import TableView
from gui.actions_panel import ActionsPanel
from gui.table_model import TableModel
from gui.dashboard import DashboardWidget
from db.database import Database
from gui.actions_handler import ActionsHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #e8e8e8;")
        self.setWindowTitle("АРМ управления тестированием")
        self.setMinimumSize(1000, 700)
        
        self.db = Database("arm_testing.db")
        self.model = TableModel(self.db)
        self.current_project = None
        
        self.setup_ui()
        self.connect_signals()
        self.load_data()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        self.dashboard = DashboardWidget()
        layout.addWidget(self.dashboard)
        
        self.filters = FiltersBar()
        layout.addWidget(self.filters)
        
        self.table = TableView()
        layout.addWidget(self.table)
        
        self.actions = ActionsPanel()
        layout.addWidget(self.actions)

        self.actions_handler = ActionsHandler(self, self.db, self.table, self.load_data)
    
    def connect_signals(self):
        self.filters.filters_changed.connect(self.load_data)
        self.table.item_selected.connect(self.on_project_selected)
        
        self.actions.add_project_clicked.connect(self.actions_handler.add_project)
        self.actions.edit_project_clicked.connect(self.actions_handler.edit_project)
        self.actions.delete_project_clicked.connect(self.actions_handler.delete_project)
        self.actions.add_test_clicked.connect(self.actions_handler.add_test)
        self.actions.edit_test_clicked.connect(self.actions_handler.edit_test)
        self.actions.delete_test_clicked.connect(self.actions_handler.delete_test)
        self.actions.run_selected_clicked.connect(self.actions_handler.run_selected)
        self.actions.run_all_clicked.connect(self.actions_handler.run_all)
        self.actions.history_clicked.connect(self.actions_handler.show_history)
        self.actions.analytics_clicked.connect(self.actions_handler.show_analytics)
        self.table.item_double_clicked.connect(self.actions_handler.show_history)            
        
    def on_project_selected(self, selected_item):
        self.current_project = selected_item
        self.update_dashboard()
    
    def load_data(self):
        filters = self.filters.get_values()
        data = self.model.load(filters)
        self.table.set_data(data)
        
        projects = self.db.get_projects()
        self.filters.set_projects(projects)
        
        groups = sorted(set(item.get("group") for item in data if item.get("group")))
        self.filters.set_groups(groups)
        
        self.update_dashboard()
    
    def get_current_project_data(self):
        """Получает данные о текущем проекте (выбранном в таблице)"""
        current_project_name = "--"
        active_tests_count = 0
        last_run_info = None
        dynamic_stats = None
        failed_tests = []
        flaky_tests = []
        slow_tests = []
        
        if self.current_project:
            current_project_name = self.current_project.get("project_name", "--")
            current_root_path = self.current_project.get("root_path", "")
            
            if current_root_path:
                from pathlib import Path
                from db.database import Database
                from db.analytics import AnalyticsRepo
                
                local_db_path = Path(current_root_path) / ".arm" / "arm_testing.db"
                if local_db_path.exists():
                    local_db = Database(str(local_db_path))
                    analytics = AnalyticsRepo(local_db)
                    
                    test_cases = local_db.get_test_cases(1)
                    active_tests_count = sum(1 for t in test_cases if t[4] == 1)
                    last_run_info = analytics.get_last_run_info()
                    dynamic_stats = analytics.get_dynamic_stats()
                    failed_tests = analytics.get_failed_tests_last_run()
                    flaky_tests = analytics.get_flaky_tests()
                    slow_tests = analytics.get_slow_tests()
        
        return {
            "project_name": current_project_name,
            "active_tests": active_tests_count,
            "last_run": last_run_info,
            "dynamic_stats": dynamic_stats,
            "failed_tests": failed_tests,
            "flaky_tests": flaky_tests,
            "slow_tests": slow_tests
        }
    
    def get_global_stats(self, projects):
        """Собирает глобальную статистику по всем проектам"""
        total_runs = 0
        total_passed = 0
        total_tests = 0
        last_runs = []
        
        for proj_id, proj_name, _, root_path in projects:
            if not root_path:
                continue
            
            from pathlib import Path
            from db.database import Database
            
            local_db_path = Path(root_path) / ".arm" / "arm_testing.db"
            if not local_db_path.exists():
                continue
            
            local_db = Database(str(local_db_path))
            runs = local_db.get_test_runs(1)
            total_runs += len(runs)
            
            for run in runs[:5]:
                run_id, start_time, end_time, status = run
                last_runs.append((proj_name, status, run_id))
                results = local_db.get_test_results_by_run(run_id)
                total_tests += len(results)
                passed = sum(1 for r in results if r[2] == "passed")
                total_passed += passed
        
        last_runs.sort(key=lambda x: x[2], reverse=True)
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "projects_count": len(projects),
            "total_runs": total_runs,
            "pass_rate": pass_rate,
            "last_runs": last_runs[:3]
        }
    
    def update_dashboard(self):
        projects = self.db.get_projects()
        
        current_data = self.get_current_project_data()
        global_data = self.get_global_stats(projects)
        
        self.dashboard.update_stats(
            global_data["projects_count"],
            global_data["total_runs"],
            global_data["pass_rate"],
            global_data["last_runs"],
            project_name=current_data["project_name"],
            active_tests=current_data["active_tests"],
            last_run=current_data["last_run"],
            dynamic_stats=current_data["dynamic_stats"],
            failed_tests=current_data["failed_tests"],
            flaky_tests=current_data["flaky_tests"],
            slow_tests=current_data["slow_tests"]
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())