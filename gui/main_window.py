import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from gui.add_project_dialog import AddProjectDialog
from gui.test_manager import TestManagerWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("АРМ управления тестированием")
        self.setMinimumSize(800, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Кнопки
        self.btn_load = QPushButton("Загрузить проекты")
        layout.addWidget(self.btn_load)

        # Панель фильтра
        filter_layout = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Фильтр по названию...")
        self.btn_reset_filter = QPushButton("Сбросить")
        filter_layout.addWidget(QLabel("Поиск:"))
        filter_layout.addWidget(self.filter_edit)
        filter_layout.addWidget(self.btn_reset_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.btn_add = QPushButton("Добавить проект")
        layout.addWidget(self.btn_add)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Название"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Связи
        self.btn_load.clicked.connect(self.load_projects)
        self.btn_add.clicked.connect(self.add_project)
        self.table.doubleClicked.connect(self.open_test_manager)
        self.filter_edit.textChanged.connect(self.apply_filter)
        self.btn_reset_filter.clicked.connect(self.reset_filter)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_projects)

        self.all_projects = []  # храним все проекты для фильтрации и сортировки
        self.load_projects()

    def load_projects(self):
        from db.database import Database
        db = Database("arm_testing.db")
        
        projects = db.get_projects()
        if not projects:
            db.add_project("Тестовый проект", "Автоматически созданный проект для проверки")
            projects = db.get_projects()
        
        self.all_projects = list(projects)
        self.display_projects(self.all_projects)

    def display_projects(self, projects):
        self.table.setRowCount(len(projects))
        for row, (pid, name, desc) in enumerate(projects):
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
        self.display_projects(self.all_projects)

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
        self.apply_filter()  # сохраняем фильтр при сортировке

    def add_project(self):
        dialog = AddProjectDialog(self)
        if dialog.exec() == AddProjectDialog.DialogCode.Accepted:
            name, desc = dialog.get_data()
            if not name:
                QMessageBox.warning(self, "Ошибка", "Название проекта не может быть пустым.")
                return
            from db.database import Database
            db = Database("arm_testing.db")
            db.add_project(name, desc)
            self.load_projects()

    def open_test_manager(self, index):
        current_row = index.row()
        project_id = int(self.table.item(current_row, 0).text())
        project_name = self.table.item(current_row, 1).text()
        self.test_manager_window = TestManagerWindow(project_id, project_name)
        self.test_manager_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())