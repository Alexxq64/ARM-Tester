"""Основной виджет дашборда с переключателем режимов"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QCursor

from gui.dashboard.compact_mode import CompactModeWidget
from gui.dashboard.alerts_mode import AlertsModeWidget


class DashboardWidget(QWidget):
    filter_by_status = Signal(str)
    filter_by_test = Signal(str)
    re_run_test = Signal(int)
    show_test_history = Signal(int)
    show_analytics = Signal()
    show_history = Signal()
    project_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = "compact"
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Верхняя панель
        top = QHBoxLayout()
        self.title = QLabel("📊 Состояние")
        self.title.setStyleSheet("font-weight: bold; font-size: 14px;")
        top.addWidget(self.title)
        top.addStretch()
        
        self.btn_compact = self._make_toggle("📊", "Компактный режим")
        self.btn_alerts = self._make_toggle("🚨", "Режим тревог")
        top.addWidget(self.btn_compact)
        top.addWidget(self.btn_alerts)
        layout.addLayout(top)
        
        # Контент
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content)
        
        # Сигналы
        self.btn_compact.clicked.connect(lambda: self.switch_mode("compact"))
        self.btn_alerts.clicked.connect(lambda: self.switch_mode("alerts"))
        
        self.switch_mode("compact")
    
    def _make_toggle(self, icon, tip):
        btn = QPushButton(icon)
        btn.setFixedSize(32, 32)
        btn.setToolTip(tip)
        btn.setCheckable(True)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return btn
    
    def switch_mode(self, mode):
        self.current_mode = mode
        self.btn_compact.setChecked(mode == "compact")
        self.btn_alerts.setChecked(mode == "alerts")
        self._update_button_styles()
        
        # Очищаем и создаём новый виджет
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if mode == "compact":
            self.title.setText("📊 Компактный режим")
            self.mode_widget = CompactModeWidget()
            self._forward_signals(self.mode_widget)
            self.content_layout.addWidget(self.mode_widget)
        else:
            self.title.setText("🚨 Центр тревог")
            self.mode_widget = AlertsModeWidget()
            self._forward_signals(self.mode_widget)
            self.content_layout.addWidget(self.mode_widget)
    
    def _forward_signals(self, widget):
        widget.filter_by_status.connect(self.filter_by_status.emit)
        widget.filter_by_test.connect(self.filter_by_test.emit)
        widget.re_run_test.connect(self.re_run_test.emit)
        widget.show_test_history.connect(self.show_test_history.emit)
    
    def _update_button_styles(self):
        active = "background:#0078d4; color:white; border:none; border-radius:4px;"
        inactive = "background:#e0e0e0; color:#666; border:none; border-radius:4px;"
        self.btn_compact.setStyleSheet(active if self.current_mode == "compact" else inactive)
        self.btn_alerts.setStyleSheet(active if self.current_mode == "alerts" else inactive)
    
    def update_stats(self, projects_count, runs_count, pass_rate, last_runs, **kwargs):
        if hasattr(self, 'mode_widget'):
            self.mode_widget.update_data(**kwargs)