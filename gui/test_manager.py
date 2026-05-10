import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, 
                               QMessageBox, QHBoxLayout, QLineEdit, QComboBox, QLabel)
from PySide6.QtCore import Qt

from db.database import Database
from gui.add_edit_test_dialog import AddEditTestDialog
from config import PROJECT_ROOT
from gui.runs_history_window import RunsHistoryWindow
from gui.test_runner import TestRunner

class TestManagerWindow(QMainWindow):
    def __init__(self, project_id, project_name):
        super().__init__()
        self.project_id = project_id
        self.project_name = project_name
        self.setWindowTitle(f"Тесты проекта: {project_name}")
        self.setMinimumSize(900, 500)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Группа", "Путь", "Активен"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Панель фильтров
        filter_layout = QHBoxLayout()
        self.filter_name = QLineEdit()
        self.filter_name.setPlaceholderText("Фильтр по названию...")
        self.filter_group = QComboBox()
        self.filter_group.addItem("Все группы")
        self.filter_active = QComboBox()
        self.filter_active.addItems(["Все", "Активные", "Неактивные"])
        self.btn_reset_filter = QPushButton("Сбросить")
        
        filter_layout.addWidget(QLabel("Название:"))
        filter_layout.addWidget(self.filter_name)
        filter_layout.addWidget(QLabel("Группа:"))
        filter_layout.addWidget(self.filter_group)
        filter_layout.addWidget(QLabel("Активен:"))
        filter_layout.addWidget(self.filter_active)
        filter_layout.addWidget(self.btn_reset_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить тест")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_refresh = QPushButton("Обновить")
        self.btn_run_selected = QPushButton("Запустить выбранные")
        self.btn_run_all = QPushButton("Запустить все активные")
        self.btn_history = QPushButton("История запусков")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_run_selected)
        btn_layout.addWidget(self.btn_run_all)
        btn_layout.addWidget(self.btn_history)
        layout.addLayout(btn_layout)

        # Связи
        self.btn_add.clicked.connect(self.add_test)
        self.btn_edit.clicked.connect(self.edit_test)
        self.btn_delete.clicked.connect(self.delete_test)
        self.btn_refresh.clicked.connect(self.load_tests)
        self.btn_run_selected.clicked.connect(self.run_selected_tests)
        self.btn_run_all.clicked.connect(self.run_all_active_tests)
        self.btn_history.clicked.connect(self.open_history)
        self.table.doubleClicked.connect(self.edit_test)
        
        self.filter_name.textChanged.connect(self.apply_filter)
        self.filter_group.currentTextChanged.connect(self.apply_filter)
        self.filter_active.currentTextChanged.connect(self.apply_filter)
        self.btn_reset_filter.clicked.connect(self.reset_filter)
        
        # Сортировка
        self.table.horizontalHeader().sectionClicked.connect(self.sort_tests)
        
        self.all_tests = []
        self.load_tests()

    def load_tests(self):
        db = Database("arm_testing.db")
        tests = db.get_test_cases(self.project_id)
        self.all_tests = list(tests)
        groups = sorted(set(t[2] for t in self.all_tests if t[2]))
        self.filter_group.clear()
        self.filter_group.addItem("Все группы")
        self.filter_group.addItems(groups)
        self.apply_filter()

    def display_tests(self, tests):
        self.table.setRowCount(len(tests))
        for row, (test_id, name, group_name, test_path, is_active) in enumerate(tests):
            self.table.setItem(row, 0, QTableWidgetItem(str(test_id)))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(group_name if group_name else ""))
            self.table.setItem(row, 3, QTableWidgetItem(test_path))
            self.table.setItem(row, 4, QTableWidgetItem("Да" if is_active else "Нет"))

    def apply_filter(self):
        name_filter = self.filter_name.text().lower()
        group_filter = self.filter_group.currentText()
        active_filter = self.filter_active.currentText()
        
        filtered = self.all_tests.copy()
        
        if name_filter:
            filtered = [t for t in filtered if name_filter in t[1].lower()]
        if group_filter != "Все группы":
            filtered = [t for t in filtered if t[2] == group_filter]
        if active_filter == "Активные":
            filtered = [t for t in filtered if t[4] == 1]
        elif active_filter == "Неактивные":
            filtered = [t for t in filtered if t[4] == 0]
        
        self.display_tests(filtered)

    def reset_filter(self):
        self.filter_name.clear()
        self.filter_group.setCurrentIndex(0)
        self.filter_active.setCurrentIndex(0)

    def sort_tests(self, col):
        if not self.all_tests:
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
            self.all_tests.sort(key=lambda x: int(x[0]), reverse=self._sort_order)
        elif col == 1:
            self.all_tests.sort(key=lambda x: x[1].lower(), reverse=self._sort_order)
        elif col == 2:
            self.all_tests.sort(key=lambda x: (x[2] or "").lower(), reverse=self._sort_order)
        elif col == 3:
            self.all_tests.sort(key=lambda x: x[3].lower(), reverse=self._sort_order)
        elif col == 4:
            self.all_tests.sort(key=lambda x: x[4], reverse=self._sort_order)
        self.display_tests(self.all_tests)
        self.apply_filter()

    def get_selected_test_ids(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return []
        test_ids = []
        for index in selected_rows:
            test_id = int(self.table.item(index.row(), 0).text())
            test_ids.append(test_id)
        return test_ids

    def add_test(self):
        dialog = AddEditTestDialog(self, edit_mode=False)
        if dialog.exec() == AddEditTestDialog.DialogCode.Accepted:
            data = dialog.get_data()
            db = Database("arm_testing.db")
            path = Path(data["test_path"])
            try:
                rel_path = str(path.relative_to(PROJECT_ROOT))
            except ValueError:
                rel_path = data["test_path"]
            db.add_test_case(self.project_id, data["name"], rel_path, data["group_name"], data["is_active"])
            self.load_tests()

    def edit_test(self):
        test_ids = self.get_selected_test_ids()
        if len(test_ids) != 1:
            QMessageBox.warning(self, "Ошибка", "Выберите один тест для редактирования.")
            return
        
        db = Database("arm_testing.db")
        test_data = db.get_test_case_by_id(test_ids[0])
        if not test_data:
            QMessageBox.warning(self, "Ошибка", "Тест не найден.")
            return
        
        dialog = AddEditTestDialog(self, edit_mode=True, test_data=test_data)
        if dialog.exec() == AddEditTestDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            db.update_test_case(test_ids[0], new_data["name"], new_data["group_name"], new_data["test_path"], new_data["is_active"])
            self.load_tests()

    def delete_test(self):
        test_ids = self.get_selected_test_ids()
        if not test_ids:
            QMessageBox.warning(self, "Ошибка", "Выберите тест для удаления.")
            return
        
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить выбранные тесты ({len(test_ids)} шт.)?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db = Database("arm_testing.db")
            for tid in test_ids:
                db.delete_test_case(tid)
            self.load_tests()

    def run_selected_tests(self):
        test_ids = self.get_selected_test_ids()
        if not test_ids:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один тест.")
            return
        TestRunner.run_tests(self, self.project_id, test_ids)

    def run_all_active_tests(self):
        db = Database("arm_testing.db")
        tests = db.get_test_cases(self.project_id)
        active_ids = [t[0] for t in tests if t[4] == 1]
        if not active_ids:
            QMessageBox.information(self, "Информация", "Нет активных тестов.")
            return
        TestRunner.run_tests(self, self.project_id, active_ids)

    def open_history(self):
        history_window = RunsHistoryWindow(self.project_id, self)
        history_window.exec()