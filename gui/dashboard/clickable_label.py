"""Кликабельная метка"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QCursor


class ClickableLabel(QLabel):
    clicked = Signal()
    
    def __init__(self, text="", data=None, parent=None):
        super().__init__(text, parent)
        self.data = data
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("padding:4px 8px; border-radius:4px;")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        self.setStyleSheet("padding:4px 8px; border-radius:4px; background:#e0e0e0;")
    
    def leaveEvent(self, event):
        self.setStyleSheet("padding:4px 8px; border-radius:4px;")