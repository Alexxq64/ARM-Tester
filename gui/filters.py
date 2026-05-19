"""Виджет фильтров для TestManagerWindow"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMenu
from PySide6.QtCore import Signal, Qt


class FilterWidgets(QWidget):
    """Панель фильтров: название (QLineEdit), группа (QMenu), активен (QMenu)"""
    
    filters_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._groups = []
        self._current_group = "Все группы"
        self._current_active = "Все"
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Фильтр по названию
        layout.addWidget(QLabel("Название:"))
        self.filter_name = QLineEdit()
        self.filter_name.setPlaceholderText("Фильтр по названию...")
        self.filter_name.textChanged.connect(self._on_name_changed)
        layout.addWidget(self.filter_name)
        
        # Фильтр по группе (кнопка + меню)
        layout.addWidget(QLabel("Группа:"))
        self.group_btn = QPushButton("Все группы")
        self.group_btn.setMinimumWidth(100)
        self.group_menu = QMenu(self.group_btn)
        self.group_btn.setMenu(self.group_menu)
        self.group_btn.clicked.connect(self._show_group_menu)
        layout.addWidget(self.group_btn)
        
        # Фильтр по активности (кнопка + меню)
        layout.addWidget(QLabel("Активен:"))
        self.active_btn = QPushButton("Все")
        self.active_btn.setMinimumWidth(80)
        self.active_menu = QMenu(self.active_btn)
        self.active_btn.setMenu(self.active_menu)
        self.active_btn.clicked.connect(self._show_active_menu)
        layout.addWidget(self.active_btn)
        
        # Кнопка сброса
        self.btn_reset = QPushButton("Сбросить")
        self.btn_reset.clicked.connect(self.reset_filters)
        layout.addWidget(self.btn_reset)
        
        layout.addStretch()
    
    def set_groups(self, groups):
        """Устанавливает список групп для фильтра"""
        self._groups = sorted(groups)
    
    def _show_group_menu(self):
        self.group_menu.clear()
        # Пункт "Все группы"
        all_action = self.group_menu.addAction("Все группы")
        all_action.triggered.connect(lambda: self._set_group("Все группы"))
        self.group_menu.addSeparator()
        for group in self._groups:
            action = self.group_menu.addAction(group)
            action.triggered.connect(lambda checked=False, g=group: self._set_group(g))
        self.group_menu.exec(self.group_btn.mapToGlobal(self.group_btn.rect().bottomLeft()))
    
    def _show_active_menu(self):
        self.active_menu.clear()
        for value in ["Все", "Активные", "Неактивные"]:
            action = self.active_menu.addAction(value)
            action.triggered.connect(lambda checked=False, v=value: self._set_active(v))
        self.active_menu.exec(self.active_btn.mapToGlobal(self.active_btn.rect().bottomLeft()))
    
    def _set_group(self, group):
        self._current_group = group
        self.group_btn.setText(group[:20] + ".." if len(group) > 20 else group)
        self.filters_changed.emit()
    
    def _set_active(self, active):
        self._current_active = active
        self.active_btn.setText(active)
        self.filters_changed.emit()
    
    def _on_name_changed(self):
        self.filters_changed.emit()
    
    def get_filter_values(self):
        return {
            "name": self.filter_name.text(),
            "group": self._current_group,
            "active": self._current_active,
        }
    
    def reset_filters(self):
        self.filter_name.clear()
        self._set_group("Все группы")
        self._set_active("Все")