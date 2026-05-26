# gui/analytics_chart.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use('Qt5Agg')

from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from db.database import Database

class AnalyticsChartWindow(QDialog):
    def __init__(self, project_id, db_path, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.db_path = db_path
        self.setWindowTitle("Динамика прохождения тестов")
        self.setMinimumSize(1000, 650)

        layout = QVBoxLayout(self)

        # Кнопка обновления
        self.btn_refresh = QPushButton("Обновить график")
        self.btn_refresh.clicked.connect(self.draw_chart)
        layout.addWidget(self.btn_refresh)

        # Место для графика
        self.figure = Figure(figsize=(12, 7), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.draw_chart()

    def draw_chart(self):
        db = Database(self.db_path)
        runs = db.get_test_runs(self.project_id)

        if not runs:
            QMessageBox.information(self, "Нет данных", "Нет запусков для отображения графика.")
            return

        # Собираем данные
        run_ids = []
        passed_counts = []
        failed_counts = []
        total_counts = []
        pass_rates = []
        run_labels = []

        for run_id, start_time, end_time, status in runs:
            if status == "running":
                continue
            results = db.get_test_results_by_run(run_id)
            passed = sum(1 for r in results if r[5] == "passed")
            failed = sum(1 for r in results if r[5] == "failed")
            total = passed + failed
            if total > 0:
                pass_rate = (passed / total) * 100
            else:
                pass_rate = 0

            label = f"{run_id}\n{start_time[:10]}"
            run_labels.append(label)
            passed_counts.append(passed)
            failed_counts.append(failed)
            total_counts.append(total)
            pass_rates.append(pass_rate)
            run_ids.append(run_id)

        if not run_ids:
            QMessageBox.information(self, "Нет данных", "Нет завершённых запусков для отображения графика.")
            return

        # Очищаем фигуру
        self.figure.clear()

        # Создаём две оси (первая для столбцов, вторая для линии процентов)
        ax1 = self.figure.add_subplot(111)
        ax2 = ax1.twinx()

        x = np.arange(len(run_ids))
        width = 0.6

        # Столбцы passed и failed
        bars_passed = ax1.bar(x, passed_counts, width, label="Пройдено (passed)", color="#2ecc71", edgecolor="white", linewidth=0.5)
        bars_failed = ax1.bar(x, failed_counts, width, bottom=passed_counts, label="Упало (failed)", color="#e74c3c", edgecolor="white", linewidth=0.5)

        # Линия процента прохождения
        line_pass_rate = ax2.plot(x, pass_rates, color="#3498db", marker="o", linewidth=2, markersize=6, label="Pass Rate (%)")

        # Подписи значений над столбцами
        for i, (p, f) in enumerate(zip(passed_counts, failed_counts)):
            total = p + f
            if p > 0:
                ax1.text(i, p/2, str(p), ha="center", va="center", fontsize=9, color="white", fontweight="bold")
            if f > 0:
                ax1.text(i, p + f/2, str(f), ha="center", va="center", fontsize=9, color="white", fontweight="bold")
            # Процент над столбцом
            if total > 0:
                rate = (p / total) * 100
                ax1.text(i, p + f + max(1, total*0.05), f"{rate:.0f}%", ha="center", va="bottom", fontsize=9, color="#2c3e50", fontweight="bold")

        # Настройка осей
        ax1.set_xlabel("Запуск (ID / дата)", fontsize=12)
        ax1.set_ylabel("Количество тестов", fontsize=12, color="#2c3e50")
        ax2.set_ylabel("Pass Rate (%)", fontsize=12, color="#3498db")
        ax2.tick_params(axis="y", labelcolor="#3498db")

        ax1.set_title("Динамика прохождения тестов", fontsize=14, fontweight="bold")
        ax1.set_xticks(x)
        ax1.set_xticklabels(run_labels, rotation=45, ha="right", fontsize=9)

        # Сетка
        ax1.grid(axis="y", linestyle="--", alpha=0.6)
        ax1.set_axisbelow(True)

        # Легенда
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=10)

        # Добавляем текст с трендом
        if len(pass_rates) >= 2:
            last_rate = pass_rates[-1]
            prev_rate = pass_rates[-2]
            diff = last_rate - prev_rate
            if diff > 0:
                trend_icon = "📈"
                trend_text = f"Тренд: +{diff:.1f}%"
            elif diff < 0:
                trend_icon = "📉"
                trend_text = f"Тренд: {diff:.1f}%"
            else:
                trend_icon = "➡️"
                trend_text = "Тренд: стабильно"

            # Добавляем текст в правый верхний угол
            ax1.text(0.98, 0.97, f"{trend_icon} {trend_text}",
                     transform=ax1.transAxes, fontsize=11,
                     verticalalignment="top", horizontalalignment="right",
                     bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

        self.figure.tight_layout()
        self.canvas.draw()