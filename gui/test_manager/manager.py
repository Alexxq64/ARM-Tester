import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from db.database import Database
from gui.test_manager.filters import FilterWidgets
from gui.test_manager.table import TestTable
from gui.test_manager.buttons import ButtonsPanel
from gui.test_manager.data_loader import load_tests, get_groups
from gui.test_manager.sort_filter import apply_filter, sort_tests
from gui.test_manager.operations import add_test, edit_test, delete_tests, run_tests
from gui.runs_history_window import RunsHistoryWindow


class TestManagerWindow(QMainWindow):
    def __init__(self, project_id, project_name, context=None):
        super().__init__()
        self.project_id = project_id
        self.project_name = project_name
        self.context = context
        self.all_tests = []
        self._sort_col = None
        self._sort_order = False
        
        self._setup_ui()
        self._connect_signals()
        self.reload()
    
    def _get_db(self):
        if self.context:
            print(f"DEBUG: Using context db_path: {self.context.db_path}")
            return Database(str(self.context.db_path), include_projects=False)
        print("DEBUG: No context, using fallback")
        return Database("arm_testing.db", include_projects=True)
    
    def _get_project_id_for_db(self):
        if self.context:
            return self.context.current_project_id
        return self.project_id
    
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        self.table = TestTable()
        layout.addWidget(self.table)
        
        self.filters = FilterWidgets()
        layout.addWidget(self.filters)
        
        self.buttons = ButtonsPanel()
        layout.addWidget(self.buttons)
        
        self.table.horizontalHeader().sectionClicked.connect(self._on_sort)
    
    def _connect_signals(self):
        self.filters.filters_changed.connect(self._on_filter_changed)
        self.buttons.add_clicked.connect(self._on_add)
        self.buttons.edit_clicked.connect(self._on_edit)
        self.buttons.delete_clicked.connect(self._on_delete)
        self.buttons.refresh_clicked.connect(self.reload)
        self.buttons.run_selected_clicked.connect(self._on_run_selected)
        self.buttons.run_all_clicked.connect(self._on_run_all)
        self.buttons.history_clicked.connect(self._on_history)
    
    def reload(self):
        db = self._get_db()
        project_id = self._get_project_id_for_db()
        self.all_tests = load_tests(db, project_id)
        groups = get_groups(self.all_tests)
        self.filters.set_groups(groups)
        self._apply_filter()
    
    def _on_filter_changed(self):
        self._apply_filter()
    
    def _apply_filter(self):
        filter_values = self.filters.get_filter_values()
        filtered = apply_filter(self.all_tests, filter_values)
        self.table.display_tests(filtered)
    
    def _on_sort(self, col):
        self.all_tests = sort_tests(self.all_tests, col, self._sort_col, self._sort_order)
        self._sort_col = col if self._sort_col != col else None
        self._apply_filter()
    
    def _on_add(self):
        db = self._get_db()
        project_id = self._get_project_id_for_db()
        if add_test(self, db, project_id):
            self.reload()
    
    def _on_edit(self):
        test_id = self.table.get_selected_test_id()
        if test_id:
            db = self._get_db()
            if edit_test(self, db, test_id):
                self.reload()
    
    def _on_delete(self):
        test_ids = self.table.get_selected_test_ids()
        if test_ids:
            db = self._get_db()
            if delete_tests(self, db, test_ids):
                self.reload()
    
    def _on_run_selected(self):
        test_ids = self.table.get_selected_test_ids()
        if test_ids:
            project_id = self._get_project_id_for_db()
            run_tests(self, self.context, project_id, test_ids)
    
    def _on_run_all(self):
        db = self._get_db()
        project_id = self._get_project_id_for_db()
        tests = db.get_test_cases(project_id)
        active_ids = [t[0] for t in tests if t[4] == 1]
        if active_ids:
            run_tests(self, self.context, project_id, active_ids)
    
    def _on_history(self):
        db_path = self._get_db().db_path
        project_id = self._get_project_id_for_db()
        history_window = RunsHistoryWindow(project_id, db_path, self)
        history_window.exec()