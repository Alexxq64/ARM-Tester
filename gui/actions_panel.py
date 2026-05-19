from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal


class ActionsPanel(QWidget):
    add_project_clicked = Signal()
    edit_project_clicked = Signal()
    delete_project_clicked = Signal()
    add_test_clicked = Signal()
    edit_test_clicked = Signal()
    delete_test_clicked = Signal()
    run_selected_clicked = Signal()
    run_all_clicked = Signal()
    history_clicked = Signal()
    analytics_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Проекты
        self.btn_add_project = QPushButton("+ Добавить проект")
        self.btn_edit_project = QPushButton("✎ Редактировать проект")
        self.btn_delete_project = QPushButton("✖ Удалить проект")
        
        # Тесты
        self.btn_add_test = QPushButton("+ Добавить тест")
        self.btn_edit_test = QPushButton("✎ Редактировать тест")
        self.btn_delete_test = QPushButton("✖ Удалить тест")
        
        # Запуск
        self.btn_run_selected = QPushButton("▶️ Запустить выбранные")
        self.btn_run_all = QPushButton("▶️ Запустить все активные")
        
        # История и аналитика
        self.btn_history = QPushButton("📋 История запусков")
        self.btn_analytics = QPushButton("📊 Аналитика")
        
        layout.addWidget(self.btn_add_project)
        layout.addWidget(self.btn_edit_project)
        layout.addWidget(self.btn_delete_project)
        layout.addWidget(self.btn_add_test)
        layout.addWidget(self.btn_edit_test)
        layout.addWidget(self.btn_delete_test)
        layout.addWidget(self.btn_run_selected)
        layout.addWidget(self.btn_run_all)
        layout.addWidget(self.btn_history)
        layout.addWidget(self.btn_analytics)
        layout.addStretch()
        
        # Сигналы
        self.btn_add_project.clicked.connect(self.add_project_clicked.emit)
        self.btn_edit_project.clicked.connect(self.edit_project_clicked.emit)
        self.btn_delete_project.clicked.connect(self.delete_project_clicked.emit)
        self.btn_add_test.clicked.connect(self.add_test_clicked.emit)
        self.btn_edit_test.clicked.connect(self.edit_test_clicked.emit)
        self.btn_delete_test.clicked.connect(self.delete_test_clicked.emit)
        self.btn_run_selected.clicked.connect(self.run_selected_clicked.emit)
        self.btn_run_all.clicked.connect(self.run_all_clicked.emit)
        self.btn_history.clicked.connect(self.history_clicked.emit)
        self.btn_analytics.clicked.connect(self.analytics_clicked.emit)