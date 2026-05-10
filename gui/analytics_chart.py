import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from db.database import Database

class AnalyticsChartWindow(QDialog):
    def __init__(self, project_id, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.setWindowTitle("Динамика прохождения тестов")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)

        # Кнопка обновления (на случай, если появятся новые запуски)
        self.btn_refresh = QPushButton("Обновить график")
        self.btn_refresh.clicked.connect(self.draw_chart)
        layout.addWidget(self.btn_refresh)

        # Место для графика
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.draw_chart()

    def draw_chart(self):
        db = Database("arm_testing.db")
        runs = db.get_test_runs(self.project_id)

        if not runs:
            QMessageBox.information(self, "Нет данных", "Нет запусков для отображения графика.")
            return

        # Собираем данные для графика
        run_ids = []
        passed_counts = []
        failed_counts = []
        statuses = []

        for run_id, start_time, end_time, status in runs:
            # Пропускаем незавершённые запуски
            if status == "running":
                continue
            # Получаем результаты для каждого запуска
            results = db.get_test_results_by_run(run_id)
            passed = sum(1 for r in results if r[2] == "passed")
            failed = sum(1 for r in results if r[2] == "failed")
            # Показываем номер запуска (первые 20 символов даты вместо ID - для наглядности)
            label = f"{run_id}\n{start_time[:10]}"  # ID и дата
            run_ids.append(label)
            passed_counts.append(passed)
            failed_counts.append(failed)
            statuses.append(status)

        if not run_ids:
            QMessageBox.information(self, "Нет данных", "Нет завершённых запусков для отображения графика.")
            return

        # Рисуем график
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        x = range(len(run_ids))
        width = 0.35

        ax.bar(x, passed_counts, width, label="Пройдено (passed)", color="green")
        ax.bar(x, failed_counts, width, bottom=passed_counts, label="Упало (failed)", color="red")

        ax.set_xlabel("Запуск (ID / дата)")
        ax.set_ylabel("Количество тестов")
        ax.set_title("Динамика прохождения тестов")
        ax.set_xticks(x)
        ax.set_xticklabels(run_ids, rotation=45, ha="right", fontsize=8)
        ax.legend()

        self.figure.tight_layout()
        self.canvas.draw()