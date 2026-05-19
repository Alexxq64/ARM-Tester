"""Таблица с тестами"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt


class TestTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["ID", "Название", "Группа", "Путь", "Активен"])
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    
    def display_tests(self, tests):
        self.setRowCount(len(tests))
        for row, (test_id, name, group_name, test_path, is_active) in enumerate(tests):
            self.setItem(row, 0, QTableWidgetItem(str(test_id)))
            self.setItem(row, 1, QTableWidgetItem(name))
            self.setItem(row, 2, QTableWidgetItem(group_name if group_name else ""))
            self.setItem(row, 3, QTableWidgetItem(test_path))
            self.setItem(row, 4, QTableWidgetItem("Да" if is_active else "Нет"))
    
    def get_selected_test_ids(self):
        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return []
        test_ids = []
        for index in selected_rows:
            test_id = int(self.item(index.row(), 0).text())
            test_ids.append(test_id)
        return test_ids
    
    def get_selected_test_id(self):
        ids = self.get_selected_test_ids()
        return ids[0] if ids else None