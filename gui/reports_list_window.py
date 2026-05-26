from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QFileDialog
from PySide6.QtCore import Qt
from pathlib import Path
import subprocess
import os
import sys

from db.database import Database

class ReportsListWindow(QDialog):
    def __init__(self, run_id, db_path, parent=None):
        super().__init__(parent)
        self.run_id = run_id
        self.db_path = db_path
        self.setWindowTitle(f"Отчёты для запуска #{run_id}")
        self.setMinimumSize(700, 400)

        layout = QVBoxLayout(self)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Путь", "Дата создания"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Обновить")
        self.btn_open = QPushButton("Открыть")
        self.btn_delete = QPushButton("Удалить")
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

        self.btn_refresh.clicked.connect(self.load_reports)
        self.btn_open.clicked.connect(self.open_report)
        self.btn_delete.clicked.connect(self.delete_report)
        self.table.doubleClicked.connect(self.open_report)

        self.load_reports()

    def load_reports(self):
        db = Database(self.db_path)
        reports = db.get_reports_by_run(self.run_id)

        self.table.setRowCount(len(reports))
        for row, (report_id, file_path, created_at) in enumerate(reports):
            self.table.setItem(row, 0, QTableWidgetItem(str(report_id)))
            self.table.setItem(row, 1, QTableWidgetItem(file_path))
            self.table.setItem(row, 2, QTableWidgetItem(created_at))

    def get_selected_report(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return None
        report_id = int(self.table.item(selected[0].row(), 0).text())
        file_path = self.table.item(selected[0].row(), 1).text()
        return report_id, file_path

    def open_report(self):
        selected = self.get_selected_report()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите отчёт для открытия.")
            return
        
        _, file_path = selected
        
        if not Path(file_path).exists():
            QMessageBox.warning(self, "Ошибка", f"Файл не найден:\n{file_path}")
            return
        
        try:
            subprocess.run(["firefox", file_path], check=False)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл:\n{e}")

    def delete_report(self):
        selected = self.get_selected_report()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите отчёт для удаления.")
            return
        
        report_id, file_path = selected
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить отчёт #{report_id}?\nФайл: {file_path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            db = Database(self.db_path)
            db.delete_report(report_id)
            self.load_reports()