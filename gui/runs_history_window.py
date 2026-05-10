from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QHeaderView, QPushButton,
                               QDateEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QDate
from datetime import datetime, timedelta
from db.database import Database
from gui.run_results_window import RunResultsWindow

class RunsHistoryWindow(QDialog):
    def __init__(self, project_id, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.setWindowTitle("История запусков")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)

        # Панель фильтров
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Дата с:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("по:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_to)
        
        self.btn_apply = QPushButton("Применить фильтр")
        self.btn_reset = QPushButton("Сбросить")
        filter_layout.addWidget(self.btn_apply)
        filter_layout.addWidget(self.btn_reset)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Начало", "Длительность (сек)", "Статус"])
        
        # Разрешаем ручное изменение размера всех колонок
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        # Устанавливаем начальную ширину
        self.table.setColumnWidth(0, 60)   # ID
        self.table.setColumnWidth(1, 200)  # Начало
        self.table.setColumnWidth(2, 120)  # Длительность
        self.table.setColumnWidth(3, 100)  # Статус
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Кнопки действий
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Обновить")
        self.btn_show = QPushButton("Показать результаты")
        self.btn_delete = QPushButton("Удалить выбранные")
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_show)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

        # Связи
        self.btn_refresh.clicked.connect(self.load_runs)
        self.btn_show.clicked.connect(self.show_results)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_apply.clicked.connect(self.load_runs)
        self.btn_reset.clicked.connect(self.reset_filter)
        self.table.doubleClicked.connect(self.show_results)

        self.btn_analytics = QPushButton("Аналитика (график)")
        btn_layout.addWidget(self.btn_analytics)
        self.btn_analytics.clicked.connect(self.show_analytics)
        
        self.btn_reports = QPushButton("Отчёты")
        btn_layout.addWidget(self.btn_reports)
        self.btn_reports.clicked.connect(self.show_reports)

        # Сортировка по клику на заголовок
        self.table.horizontalHeader().sectionClicked.connect(self.sort_by_column)
        
        self.current_data = []  # храним текущие данные для сортировки
        self.load_runs()

    def get_filter_params(self):
        date_from = self.date_from.date().toString("yyyy-MM-dd") if self.date_from.date() else None
        date_to = self.date_to.date().toString("yyyy-MM-dd") if self.date_to.date() else None
        if date_to:
            date_to += "T23:59:59"
        if date_from:
            date_from += "T00:00:00"
        return date_from, date_to

    def reset_filter(self):
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.load_runs()

    def load_runs(self):
        db = Database("arm_testing.db")
        date_from, date_to = self.get_filter_params()
        runs = db.get_test_runs(self.project_id, date_from, date_to)

        self.current_data = []
        for run_id, start_time, end_time, status in runs:
            duration = ""
            if start_time and end_time:
                try:
                    start = datetime.fromisoformat(start_time)
                    end = datetime.fromisoformat(end_time)
                    seconds = (end - start).total_seconds()
                    duration = f"{seconds:.2f}"
                except:
                    duration = ""
            self.current_data.append((run_id, start_time, duration, status))
        
        self.display_data(self.current_data)

    def display_data(self, data):
        """Отображает данные в таблице"""
        self.table.setRowCount(len(data))
        for row, (run_id, start_time, duration, status) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(run_id)))
            self.table.setItem(row, 1, QTableWidgetItem(start_time))
            self.table.setItem(row, 2, QTableWidgetItem(duration))
            self.table.setItem(row, 3, QTableWidgetItem(status))

    def sort_by_column(self, col):
        """Сортировка по выбранной колонке"""
        if not self.current_data:
            return
        
        # Определяем ключ для сортировки в зависимости от колонки
        if col == 0:  # ID
            key = lambda x: int(x[0])
        elif col == 1:  # Начало
            key = lambda x: x[1]
        elif col == 2:  # Длительность
            key = lambda x: float(x[2]) if x[2] else 0
        elif col == 3:  # Статус
            key = lambda x: x[3]
        else:
            return
        
        # Сортировка (чередуем порядок при повторном клике)
        if not hasattr(self, '_sort_col'):
            self._sort_col = None
            self._sort_order = False
        
        if self._sort_col == col:
            self._sort_order = not self._sort_order
        else:
            self._sort_col = col
            self._sort_order = False
        
        self.current_data.sort(key=key, reverse=self._sort_order)
        self.display_data(self.current_data)

    def get_selected_run_ids(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return []
        run_ids = []
        for idx in selected:
            run_id = int(self.table.item(idx.row(), 0).text())
            run_ids.append(run_id)
        return run_ids

    def show_results(self):
        run_ids = self.get_selected_run_ids()
        if len(run_ids) != 1:
            QMessageBox.warning(self, "Ошибка", "Выберите один запуск для просмотра результатов.")
            return
        results_window = RunResultsWindow(run_ids[0], self)
        results_window.exec()

    def delete_selected(self):
        run_ids = self.get_selected_run_ids()
        if not run_ids:
            QMessageBox.warning(self, "Ошибка", "Выберите запуски для удаления.")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить выбранные запуски ({len(run_ids)} шт.)? Все результаты этих запусков также будут удалены.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            db = Database("arm_testing.db")
            for run_id in run_ids:
                db.delete_test_run(run_id)
            self.load_runs()

    def show_analytics(self):
        from gui.analytics_chart import AnalyticsChartWindow
        analytics_window = AnalyticsChartWindow(self.project_id, self)
        analytics_window.exec()

    def show_reports(self):
        run_ids = self.get_selected_run_ids()
        if len(run_ids) != 1:
            QMessageBox.warning(self, "Ошибка", "Выберите один запуск для просмотра отчётов.")
            return
        from gui.reports_list_window import ReportsListWindow
        reports_window = ReportsListWindow(run_ids[0], self)
        reports_window.exec()