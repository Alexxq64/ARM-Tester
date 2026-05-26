"""Карточка для режима тревог"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Signal, Qt


class AlertCard(QFrame):
    item_clicked = Signal(str, int)  # тип, test_id
    
    def __init__(self, title, card_type, parent=None):
        super().__init__(parent)
        self.card_type = card_type
        self.title = title
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame{background:white;border:1px solid #ddd;border-radius:8px;margin:2px;}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-weight:bold;font-size:13px;padding:5px;background:#f0f0f0;border-radius:4px;")
        layout.addWidget(title_label)
        
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setSpacing(5)
        self.list_layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.list_widget)
    
    def set_items(self, items):
        # Очищаем
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not items:
            placeholder = QLabel("✅ Нет проблем")
            placeholder.setStyleSheet("color:#888;padding:10px;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(placeholder)
            return
        
        for item in items:
            self.list_layout.addWidget(self._make_item(item))
    
    def _make_item(self, item):
        from gui.dashboard.clickable_label import ClickableLabel
        
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 2, 0, 2)
        
        name = ClickableLabel(item.get('test_name', '--')[:40])
        name.clicked.connect(lambda: self.item_clicked.emit('test', item.get('test_id', 0)))
        
        info = QLabel(self._get_info_text(item))
        info.setStyleSheet("color:#666;font-size:11px;")
        
        run_btn = ClickableLabel("▶️")
        run_btn.clicked.connect(lambda: self.item_clicked.emit('rerun', item.get('test_id', 0)))
        
        layout.addWidget(name)
        layout.addStretch()
        layout.addWidget(info)
        layout.addWidget(run_btn)
        
        return widget
    
    def _get_info_text(self, item):
        if self.card_type == "failed":
            return f"{item.get('execution_time', 0):.1f}s"
        elif self.card_type == "flaky":
            return f"{item.get('change_count', 0)} изм."
        else:
            return f"{item.get('execution_time', 0):.1f}s"