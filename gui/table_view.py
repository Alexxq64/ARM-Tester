from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt


class TableView(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["Проект", "Тест", "Группа", "Последний запуск", "Статус", "Ошибка"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        
        # Включаем сортировку
        self.setSortingEnabled(True)
    
    def set_data(self, data):
        self.setSortingEnabled(False)  # отключаем сортировку во время загрузки
        self.setRowCount(len(data))
        for row, item in enumerate(data):
            self.setItem(row, 0, QTableWidgetItem(item.get("project_name", "")))
            self.setItem(row, 1, QTableWidgetItem(item.get("test_name", "")))
            self.setItem(row, 2, QTableWidgetItem(item.get("group", "")))
            
            last_time = item.get("last_run", "")
            if last_time:
                last_time = last_time[:19]
            self.setItem(row, 3, QTableWidgetItem(last_time))
            
            status = item.get("status", "")
            status_item = QTableWidgetItem(status)
            if status == "passed":
                status_item.setForeground(Qt.GlobalColor.green)
            elif status == "failed":
                status_item.setForeground(Qt.GlobalColor.red)
            self.setItem(row, 4, status_item)
            
            error = item.get("error", "")[:100]
            self.setItem(row, 5, QTableWidgetItem(error))
        
        self.setSortingEnabled(True)  # включаем обратно
    
    def get_selected_item(self):
        row = self.currentRow()
        if row < 0:
            return None
        return {
            "project_name": self.item(row, 0).text(),
            "test_name": self.item(row, 1).text(),
        }
    
    def get_selected_test_ids(self):
        selected = self.selectionModel().selectedRows()
        return [index.row() for index in selected]