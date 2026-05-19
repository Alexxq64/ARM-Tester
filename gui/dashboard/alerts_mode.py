"""Режим тревог — три карточки с проблемными тестами"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PySide6.QtCore import Signal

from gui.dashboard.alert_card import AlertCard


class AlertsModeWidget(QWidget):
    filter_by_status = Signal(str)
    filter_by_test = Signal(str)
    re_run_test = Signal(int)
    show_test_history = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)
        
        self.failed_card = AlertCard("🚨 Упавшие тесты (последний запуск)", "failed")
        self.flaky_card = AlertCard("⚠️ Нестабильные тесты", "flaky")
        self.slow_card = AlertCard("🐢 Долгие тесты", "slow")
        
        self.failed_card.item_clicked.connect(self._on_item_clicked)
        self.flaky_card.item_clicked.connect(self._on_item_clicked)
        self.slow_card.item_clicked.connect(self._on_item_clicked)
        
        content_layout.addWidget(self.failed_card)
        content_layout.addWidget(self.flaky_card)
        content_layout.addWidget(self.slow_card)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _on_item_clicked(self, action, test_id):
        if action == 'rerun':
            self.re_run_test.emit(test_id)
        elif action == 'test':
            self.show_test_history.emit(test_id)
    
    def update_data(self, failed_tests=None, flaky_tests=None, slow_tests=None, **kwargs):
        if failed_tests is not None:
            self.failed_card.set_items(failed_tests)
        if flaky_tests is not None:
            self.flaky_card.set_items(flaky_tests)
        if slow_tests is not None:
            self.slow_card.set_items(slow_tests)