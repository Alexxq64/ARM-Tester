"""Виджет дашборда для главного окна"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class DashboardWidget(QWidget):
    """Дашборд с общей статистикой по всем проектам"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_stats(None, None, None, None)
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Карточка 1: Проекты
        self.card_projects = self._create_card("Проектов", "0")
        layout.addWidget(self.card_projects)
        
        # Карточка 2: Запуски
        self.card_runs = self._create_card("Запусков", "0")
        layout.addWidget(self.card_runs)
        
        # Карточка 3: Pass Rate
        self.card_passrate = self._create_card("Pass Rate", "0%")
        layout.addWidget(self.card_passrate)
        
        # Карточка 4: Последние запуски (заглушка, обновляется отдельно)
        self.card_last = self._create_card("Последние запуски", "—", is_last=True)
        layout.addWidget(self.card_last)
        
        layout.addStretch()
    
    def _create_card(self, title, value, is_last=False):
        """Создаёт карточку с заголовком и значением"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setFixedWidth(180 if not is_last else 250)
        card.setFixedHeight(100)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #666; font-size: 12px;")
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setBold(True)
        value_label.setFont(value_font)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        if is_last:
            # Для последних запусков храним отдельный лейбл
            self.last_runs_label = value_label
        
        return card
    
    def update_stats(self, projects_count, runs_count, pass_rate, last_runs):
        print(f"DEBUG dashboard: last_runs = {last_runs}")
        
        # Обновляем карточки
        self.card_projects.findChild(QLabel, "value") or self._update_card_value(
            self.card_projects, str(projects_count if projects_count is not None else 0)
        )
        self._update_card_value(self.card_runs, str(runs_count if runs_count is not None else 0))
        
        pass_text = f"{pass_rate:.1f}%" if pass_rate is not None else "0%"
        self._update_card_value(self.card_passrate, pass_text)
        
        # Обновляем последние запуски
        if last_runs:
            lines = []
            for proj_name, status, _ in last_runs[:3]:
                status_icon = "✅" if status == "passed" else "❌"
                # Обрезаем длинные имена
                short_name = proj_name[:20] + ".." if len(proj_name) > 20 else proj_name
                lines.append(f"{status_icon} {short_name}")
            text = "\n".join(lines)
        else:
            text = "Нет запусков"
        
        self._update_card_value(self.card_last, text, is_last=True)
    
    def _update_card_value(self, card, value, is_last=False):
        for child in card.findChildren(QLabel):
            if child.font().pointSize() == 18 or is_last:
                child.setText(value)
                if is_last:
                    child.setStyleSheet("font-size: 11px;")
        card.update()  # принудительная перерисовка