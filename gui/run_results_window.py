from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLabel, QHBoxLayout, QPushButton, 
                               QFileDialog, QMessageBox, QMenu)
from PySide6.QtCore import Qt
from pathlib import Path
from datetime import datetime

from reports.report_generator import ReportGenerator
from db.database import Database


class RunResultsWindow(QDialog):
    def __init__(self, run_id, db_path, parent=None):
        super().__init__(parent)
        self.run_id = run_id
        self.db_path = db_path
        self.setWindowTitle(f"Результаты #{run_id}")
        self.setMinimumSize(900, 500)
        self.resize(1000, 600)
        self.all_results = []
        self._current_status = "Все"

        layout = QVBoxLayout(self)

        # Панель фильтра — кнопка с меню вместо комбобокса
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Статус:"))
        
        self.status_btn = QPushButton("Все")
        self.status_btn.setMinimumWidth(80)
        self.status_menu = QMenu(self.status_btn)
        self.status_btn.setMenu(self.status_menu)
        self.status_btn.clicked.connect(self._show_status_menu)
        filter_layout.addWidget(self.status_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Таблица результатов
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Тест", "Файл", "Статус", "Ошибка"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.close)
        self.btn_save_report = QPushButton("Сохранить отчёт")
        self.btn_save_report.clicked.connect(self.save_report)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save_report)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        # Сортировка
        self.table.horizontalHeader().sectionClicked.connect(self.sort_results)

        self.load_results(run_id)

    def _show_status_menu(self):
        self.status_menu.clear()
        for value in ["Все", "passed", "failed"]:
            action = self.status_menu.addAction(value)
            action.triggered.connect(lambda checked=False, v=value: self._set_status(v))
        self.status_menu.exec(self.status_btn.mapToGlobal(self.status_btn.rect().bottomLeft()))

    def _set_status(self, status):
        self._current_status = status
        self.status_btn.setText(status)
        self.apply_filter()

    def load_results(self, run_id):
        db = Database(self.db_path)
        results = db.get_test_results_by_run(run_id)
        self.all_results = list(results)
        self.apply_filter()

    def apply_filter(self):
        if self._current_status == "Все":
            filtered = self.all_results
        else:
            filtered = [r for r in self.all_results if r[2] == self._current_status]
        self.display_results(filtered)

    def display_results(self, results):
        self.table.setRowCount(len(results))
        for row, (func_name, file_path, status, error) in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(func_name if func_name else "?"))
            self.table.setItem(row, 1, QTableWidgetItem(file_path))
            self.table.setItem(row, 2, QTableWidgetItem(status))
            self.table.setItem(row, 3, QTableWidgetItem(error if error else ""))

    def sort_results(self, col):
        if not self.all_results:
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
            self.all_results.sort(key=lambda x: (x[0] or "").lower(), reverse=self._sort_order)
        elif col == 1:
            self.all_results.sort(key=lambda x: x[1].lower(), reverse=self._sort_order)
        elif col == 2:
            self.all_results.sort(key=lambda x: x[2].lower(), reverse=self._sort_order)
        else:
            self.all_results.sort(key=lambda x: (x[3] or "").lower(), reverse=self._sort_order)
        
        self.display_results(self.all_results)
        self.apply_filter()

    def save_report(self):
        reports_dir = Path(self.db_path).parent / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        default_path = str(reports_dir / f"report_run_{self.run_id}.html")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчёт", default_path, "HTML files (*.html)"
        )
        
        if file_path:
            try:
                ReportGenerator.generate_report(self.run_id, file_path, self.db_path)
                db = Database(self.db_path)
                db.add_report(self.run_id, file_path, datetime.now().isoformat())
                QMessageBox.information(self, "Успех", f"Отчёт сохранён: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить отчёт:\n{str(e)}")