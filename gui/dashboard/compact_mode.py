"""Компактный режим — строка состояния"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QFrame
from PySide6.QtCore import Signal

from gui.dashboard.clickable_label import ClickableLabel


class CompactModeWidget(QWidget):
    filter_by_status = Signal(str)
    filter_by_test = Signal(str)
    re_run_test = Signal(int)
    show_test_history = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setStyleSheet("QFrame{background:#f5f5f5;border-radius:6px;padding:8px;}")
        
        frame_layout = QHBoxLayout(self.frame)
        frame_layout.setSpacing(15)
        
        self.project_label = ClickableLabel("📁 --")
        self.tests_label = ClickableLabel("🧪 --")
        self.results_label = ClickableLabel("✅ --/--")
        self.failed_label = ClickableLabel("⚠️ --")
        self.trend_label = ClickableLabel("📈 --")
        
        frame_layout.addWidget(self.project_label)
        frame_layout.addWidget(self._sep())
        frame_layout.addWidget(self.tests_label)
        frame_layout.addWidget(self._sep())
        frame_layout.addWidget(self.results_label)
        frame_layout.addWidget(self._sep())
        frame_layout.addWidget(self.failed_label)
        frame_layout.addWidget(self._sep())
        frame_layout.addWidget(self.trend_label)
        frame_layout.addStretch()
        
        layout.addWidget(self.frame)
        
        # Клики
        self.failed_label.clicked.connect(lambda: self.filter_by_status.emit("failed"))
        self.results_label.clicked.connect(lambda: self.filter_by_status.emit("failed"))
        self.trend_label.clicked.connect(lambda: self.filter_by_status.emit("failed"))
    
    def _sep(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(2)
        return sep
    
    def update_data(self, project_name="--", active_tests=0, last_run=None, dynamic_stats=None, **kwargs):
        self.project_label.setText(f"📁 {project_name}")
        self.tests_label.setText(f"🧪 {active_tests}")
        
        if last_run and last_run.get('total', 0) > 0:
            total = last_run['total']
            passed = last_run['passed']
            failed = last_run['failed']
            rate = int(passed / total * 100) if total > 0 else 0
            self.results_label.setText(f"✅ {passed}/{total} ({rate}%)")
            self.failed_label.setText(f"⚠️ {failed}")
        else:
            self.results_label.setText("✅ --/--")
            self.failed_label.setText("⚠️ --")
        
        if dynamic_stats:
            trend = dynamic_stats.get('trend_percent', 0)
            icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
            self.trend_label.setText(f"{icon} {trend:+.1f}%")