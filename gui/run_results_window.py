from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QHBoxLayout, QComboBox, QPushButton, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt

class RunResultsWindow(QDialog):
    def __init__(self, run_id, parent=None):
        super().__init__(parent)
        self.run_id = run_id
        self.setWindowTitle(f"Результаты #{run_id}")
        self.setMinimumSize(900, 500)
        self.resize(1000, 600)

        layout = QVBoxLayout(self)

        # Панель фильтра
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Статус:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все", "passed", "failed"])
        self.status_filter.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.status_filter)
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

        # Кнопка закрытия
        btn_layout = QHBoxLayout()
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        # Кнопка сохранения отчёта
        btn_layout = QHBoxLayout()
        self.btn_save_report = QPushButton("Сохранить отчёт")
        self.btn_save_report.clicked.connect(self.save_report)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save_report)
        layout.addLayout(btn_layout)

        # Сортировка
        self.table.horizontalHeader().sectionClicked.connect(self.sort_results)

        self.all_results = []
        self.load_results(run_id)

    def load_results(self, run_id):
        from db.database import Database
        db = Database("arm_testing.db")
        results = db.get_test_results_by_run(run_id)
        self.all_results = list(results)
        self.apply_filter()

    def apply_filter(self):
        status = self.status_filter.currentText()
        if status == "Все":
            filtered = self.all_results
        else:
            filtered = [r for r in self.all_results if r[2] == status]
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
        from PySide6.QtWidgets import QFileDialog
        from reports.report_generator import ReportGenerator
        from db.database import Database
        from datetime import datetime
        from pathlib import Path
        from config import PROJECT_ROOT
        
        # Создаём папку для отчётов, если её нет
        reports_dir = PROJECT_ROOT / "reports" / "generated"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Предлагаем сохранить в эту папку
        default_path = str(reports_dir / f"report_run_{self.run_id}.html")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчёт", default_path, "HTML files (*.html)"
        )
        
        if file_path:
            try:
                ReportGenerator.generate_report(self.run_id, file_path)
                
                # Сохраняем запись в БД
                db = Database("arm_testing.db")
                db.add_report(self.run_id, file_path, datetime.now().isoformat())
                
                QMessageBox.information(self, "Успех", f"Отчёт сохранён: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить отчёт:\n{str(e)}")