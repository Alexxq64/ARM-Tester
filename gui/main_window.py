import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QLabel, QLineEdit, QSizePolicy
from PySide6.QtCore import Qt
from gui.add_project_dialog import AddProjectDialog
from gui.test_manager import TestManagerWindow
from gui.dashboard_widget import DashboardWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("АРМ управления тестированием")
        self.setMinimumSize(800, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Добавляем дашборд
        self.dashboard = DashboardWidget()
        layout.addWidget(self.dashboard)

        # Панель фильтра — простой QLineEdit + кнопка сброса
        filter_layout = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Фильтр по названию проекта...")
        self.filter_edit.textChanged.connect(self.apply_filter)
        self.btn_reset_filter = QPushButton("Сбросить")
        self.btn_reset_filter.clicked.connect(self.reset_filter)
        filter_layout.addWidget(QLabel("Поиск:"))
        filter_layout.addWidget(self.filter_edit)
        filter_layout.addWidget(self.btn_reset_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Кнопки в горизонтальном ряду
        buttons_layout = QHBoxLayout()
        self.btn_add = QPushButton("+ Добавить проект")
        self.btn_edit = QPushButton("✎ Редактировать")
        self.btn_delete = QPushButton("✖ Удалить")
        self.btn_add.setFixedWidth(150)
        self.btn_edit.setFixedWidth(150)
        self.btn_delete.setFixedWidth(150)

        buttons_layout.addWidget(self.btn_add)
        buttons_layout.addWidget(self.btn_edit)
        buttons_layout.addWidget(self.btn_delete)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Название"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.table)

        # Связи
        self.btn_add.clicked.connect(self.add_project)
        self.btn_edit.clicked.connect(self.edit_project)
        self.btn_delete.clicked.connect(self.delete_project)
        self.table.doubleClicked.connect(self.open_test_manager)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_projects)

        self.all_projects = []
        self.load_projects()

    def load_projects(self):
        from db.database import Database
        db = Database("arm_testing.db")
        
        projects = db.get_projects()
        if not projects:
            db.add_project("Тестовый проект", "Автоматически созданный проект для проверки", "")
            projects = db.get_projects()
        
        self.all_projects = list(projects)
        self.display_projects(self.all_projects)
        self.update_dashboard()

    def display_projects(self, projects):
        self.table.setRowCount(len(projects))
        for row, (pid, name, desc, root_path) in enumerate(projects):
            self.table.setItem(row, 0, QTableWidgetItem(str(pid)))
            self.table.setItem(row, 1, QTableWidgetItem(name))

    def apply_filter(self):
        text = self.filter_edit.text().lower()
        if not text:
            self.display_projects(self.all_projects)
            return
        filtered = [p for p in self.all_projects if text in p[1].lower()]
        self.display_projects(filtered)

    def reset_filter(self):
        self.filter_edit.clear()

    def sort_projects(self, col):
        if not self.all_projects:
            return
        if not hasattr(self, '_sort_col'):
            self._sort_col = None
            self._sort_order = False
        if self._sort_col == col:
            self._sort_order = not self._sort_order
        else:
            self._sort_col = col
            self._sort_order = False
        if col == 0:
            self.all_projects.sort(key=lambda x: int(x[0]), reverse=self._sort_order)
        elif col == 1:
            self.all_projects.sort(key=lambda x: x[1].lower(), reverse=self._sort_order)
        self.display_projects(self.all_projects)
        self.apply_filter()

    def add_project(self):
        dialog = AddProjectDialog(self)
        if dialog.exec() == AddProjectDialog.DialogCode.Accepted:
            name, desc, root_path = dialog.get_data()
            if not name:
                QMessageBox.warning(self, "Ошибка", "Название проекта не может быть пустым.")
                return
            if not root_path:
                QMessageBox.warning(self, "Ошибка", "Выберите папку проекта.")
                return
            
            from pathlib import Path
            from db.database import Database
            from project_context import ProjectContext
            
            # Создаём .arm/ в папке проекта
            context = ProjectContext(Path(root_path))
            context.ensure_dirs()
            
            db = Database("arm_testing.db")
            db.add_project(name, desc, root_path)
            self.load_projects()

    def edit_project(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите проект для редактирования.")
            return
        
        row = selected[0].row()
        project_id = int(self.table.item(row, 0).text())
        
        from db.database import Database
        db = Database("arm_testing.db")
        
        projects = db.get_projects()
        project_data = None
        for p in projects:
            if p[0] == project_id:
                project_data = p
                break
        
        if not project_data:
            QMessageBox.warning(self, "Ошибка", "Проект не найден.")
            return
        
        dialog = AddProjectDialog(self, edit_mode=True, project_data=project_data)
        if dialog.exec() == AddProjectDialog.DialogCode.Accepted:
            name, desc, root_path = dialog.get_data()
            db.update_project(project_id, name, desc, root_path)
            self.load_projects()

    def delete_project(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите проект для удаления.")
            return
        
        row = selected[0].row()
        project_id = int(self.table.item(row, 0).text())
        project_name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Удалить проект \"{project_name}\"?\nВсе тесты и результаты будут удалены.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from db.database import Database
            db = Database("arm_testing.db")
            
            with db._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
                conn.commit()
            
            self.load_projects()
            QMessageBox.information(self, "Успех", f"Проект \"{project_name}\" удалён.")

    def open_test_manager(self, index):
        current_row = index.row()
        project_id = int(self.table.item(current_row, 0).text())
        
        from db.database import Database
        db = Database("arm_testing.db")
        projects = db.get_projects()
        
        project_data = None
        for p in projects:
            if p[0] == project_id:
                project_data = p
                break
        
        if not project_data:
            QMessageBox.warning(self, "Ошибка", "Проект не найден.")
            return
        
        project_id, project_name, description, root_path = project_data
        
        from pathlib import Path
        from project_context import ProjectContext
        
        if root_path:
            context = ProjectContext(Path(root_path))
            context.ensure_dirs()
        else:
            context = None
        
        self.test_manager_window = TestManagerWindow(project_id, project_name, context)
        self.test_manager_window.show()

    def update_dashboard(self):
        from db.database import Database
        db = Database("arm_testing.db")
        
        projects = db.get_projects()
        projects_count = len(projects)
        
        total_runs = 0
        total_passed = 0
        total_tests = 0
        last_runs = []
        
        for proj_id, proj_name, _, _ in projects:
            runs = db.get_test_runs(proj_id)
            total_runs += len(runs)
            
            for run in runs[:5]:
                run_id, start_time, end_time, status = run
                last_runs.append((proj_name, status, run_id))
                
                results = db.get_test_results_by_run(run_id)
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