"""Панель кнопок управления тестами"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal


class ButtonsPanel(QWidget):
    add_clicked = Signal()
    edit_clicked = Signal()
    delete_clicked = Signal()
    refresh_clicked = Signal()
    run_selected_clicked = Signal()
    run_all_clicked = Signal()
    history_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_add = QPushButton("Добавить тест")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_refresh = QPushButton("Обновить")
        self.btn_run_selected = QPushButton("Запустить выбранные")
        self.btn_run_all = QPushButton("Запустить все активные")
        self.btn_history = QPushButton("История запусков")
        
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_edit)
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.btn_refresh)
        layout.addWidget(self.btn_run_selected)
        layout.addWidget(self.btn_run_all)
        layout.addWidget(self.btn_history)
        
        self.btn_add.clicked.connect(self.add_clicked.emit)
        self.btn_edit.clicked.connect(self.edit_clicked.emit)
        self.btn_delete.clicked.connect(self.delete_clicked.emit)
        self.btn_refresh.clicked.connect(self.refresh_clicked.emit)
        self.btn_run_selected.clicked.connect(self.run_selected_clicked.emit)
        self.btn_run_all.clicked.connect(self.run_all_clicked.emit)
        self.btn_history.clicked.connect(self.history_clicked.emit)