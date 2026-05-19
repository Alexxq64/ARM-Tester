import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from gui.filters_bar import FiltersBar
from gui.table_view import TableView
from gui.actions_panel import ActionsPanel
from gui.table_model import TableModel
from gui.dashboard_widget import DashboardWidget
from gui.runs_history_window import RunsHistoryWindow
from gui.analytics_chart import AnalyticsChartWindow
from db.database import Database
from gui.actions_handler import ActionsHandler



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("АРМ управления тестированием")
        self.setMinimumSize(1000, 700)
        
        self.db = Database("arm_testing.db")
        self.model = TableModel(self.db)
        
        self._setup_ui()
        self._connect_signals()
        self.load_data()
    
    def _setup_ui(self):
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

    
    def _connect_signals(self):
        self.filters.filters_changed.connect(self.load_data)
        
        # Только подключения к actions_handler
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
    
    def load_data(self):
        filters = self.filters.get_values()
        data = self.model.load(filters)
        self.table.set_data(data)
        
        # Обновляем фильтры
        projects = self.db.get_projects()
        self.filters.set_projects(projects)
        
        # Группы из загруженных данных
        groups = sorted(set(item.get("group") for item in data if item.get("group")))
        self.filters.set_groups(groups)
        
        self._update_dashboard()
    
    def _update_dashboard(self):
        projects = self.db.get_projects()
        print(f"DEBUG: projects = {projects}")
        
        projects_count = len(projects)
        
        total_runs = 0
        total_passed = 0
        total_tests = 0
        last_runs = []
        
        for proj_id, proj_name, _, root_path in projects:
            print(f"DEBUG: checking {proj_name}, root_path={root_path}")
            if not root_path:
                print(f"DEBUG: {proj_name} skipped - no root_path")
                continue
            
            from pathlib import Path
            from db.database import Database
            
            local_db_path = Path(root_path) / ".arm" / "arm_testing.db"
            print(f"DEBUG: local_db_path = {local_db_path}, exists={local_db_path.exists()}")
            if not local_db_path.exists():
                continue
            
            local_db = Database(str(local_db_path))
            runs = local_db.get_test_runs(1)  # project_id = 1 в локальной БД
            print(f"DEBUG: {proj_name} runs count = {len(runs)}")
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
        
        self.dashboard.update_stats(projects_count, total_runs, pass_rate, last_runs[:3])
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())