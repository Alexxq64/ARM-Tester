from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu, QDateEdit, QLineEdit
from PySide6.QtCore import QDate, Signal


class FiltersBar(QWidget):
    filters_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Проект (кнопка + меню)
        layout.addWidget(QLabel("Проект:"))
        self.project_btn = QPushButton("Все проекты")
        self.project_btn.setMinimumWidth(150)
        self.project_menu = QMenu(self.project_btn)
        self.project_btn.setMenu(self.project_menu)
        self.project_btn.clicked.connect(self._show_project_menu)
        layout.addWidget(self.project_btn)
        
        # Поиск по тестам
        layout.addWidget(QLabel("Поиск:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Название теста...")
        self.search_edit.textChanged.connect(self._on_changed)
        layout.addWidget(self.search_edit)
        
        # Группа (кнопка + меню)
        layout.addWidget(QLabel("Группа:"))
        self.group_btn = QPushButton("Все группы")
        self.group_btn.setMinimumWidth(120)
        self.group_menu = QMenu(self.group_btn)
        self.group_btn.setMenu(self.group_menu)
        self.group_btn.clicked.connect(self._show_group_menu)
        layout.addWidget(self.group_btn)
        
        # Статус (кнопка + меню)
        layout.addWidget(QLabel("Статус:"))
        self.status_btn = QPushButton("Все")
        self.status_btn.setMinimumWidth(80)
        self.status_menu = QMenu(self.status_btn)
        self.status_btn.setMenu(self.status_menu)
        self.status_btn.clicked.connect(self._show_status_menu)
        layout.addWidget(self.status_btn)
        
        # Дата с
        layout.addWidget(QLabel("с:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.dateChanged.connect(self._on_changed)
        layout.addWidget(self.date_from)
        
        # Дата по
        layout.addWidget(QLabel("по:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self._on_changed)
        layout.addWidget(self.date_to)
        
        layout.addStretch()
        
        # Кнопка сброса
        self.btn_reset = QPushButton("Сбросить")
        self.btn_reset.clicked.connect(self.reset)
        layout.addWidget(self.btn_reset)
        
        self._projects = []
        self._groups = []
    
    def _on_changed(self):
        self.filters_changed.emit()
    
    def _show_project_menu(self):
        self.project_menu.clear()
        all_action = self.project_menu.addAction("Все проекты")
        all_action.triggered.connect(lambda: self._set_project("Все проекты"))
        for proj_name in self._projects:
            action = self.project_menu.addAction(proj_name)
            action.triggered.connect(lambda checked=False, name=proj_name: self._set_project(name))
        self.project_menu.exec(self.project_btn.mapToGlobal(self.project_btn.rect().bottomLeft()))
    
    def _show_group_menu(self):
        self.group_menu.clear()
        all_action = self.group_menu.addAction("Все группы")
        all_action.triggered.connect(lambda: self._set_group("Все группы"))
        for group_name in self._groups:
            action = self.group_menu.addAction(group_name)
            action.triggered.connect(lambda checked=False, name=group_name: self._set_group(name))
        self.group_menu.exec(self.group_btn.mapToGlobal(self.group_btn.rect().bottomLeft()))
    
    def _show_status_menu(self):
        self.status_menu.clear()
        for value in ["Все", "passed", "failed"]:
            action = self.status_menu.addAction(value)
            action.triggered.connect(lambda checked=False, v=value: self._set_status(v))
        self.status_menu.exec(self.status_btn.mapToGlobal(self.status_btn.rect().bottomLeft()))
    
    def _set_project(self, project_name):
        self.project_btn.setText(project_name)
        self.filters_changed.emit()
    
    def _set_group(self, group_name):
        self.group_btn.setText(group_name)
        self.filters_changed.emit()
    
    def _set_status(self, status):
        self.status_btn.setText(status)
        self.filters_changed.emit()
    
    def reset(self):
        self.search_edit.clear()
        self.project_btn.setText("Все проекты")
        self.group_btn.setText("Все группы")
        self.status_btn.setText("Все")
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.filters_changed.emit()
    
    def get_values(self):
        return {
            "search": self.search_edit.text(),
            "project": self.project_btn.text(),
            "group": self.group_btn.text(),
            "status": self.status_btn.text(),
            "date_from": self.date_from.date().toString("yyyy-MM-dd"),
            "date_to": self.date_to.date().toString("yyyy-MM-dd"),
        }
    
    def set_projects(self, projects):
        self._projects = [p[1] for p in projects]
    
    def set_groups(self, groups):
        self._groups = groups