from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QTextEdit, QDialogButtonBox, QHBoxLayout, 
                               QPushButton, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from pathlib import Path


class AddProjectDialog(QDialog):
    def __init__(self, parent=None, edit_mode=False, project_data=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #e0e0e0;")
        self.edit_mode = edit_mode
        self.project_data = project_data  # (project_id, name, description, root_path)
        
        if edit_mode:
            self.setWindowTitle("Редактировать проект")
        else:
            self.setWindowTitle("Добавить проект")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Название
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название проекта")
        form.addRow("Название:", self.name_edit)
        
        # Папка проекта
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Выберите папку с проектом")
        self.path_edit.setReadOnly(True)
        self.btn_browse = QPushButton("Обзор")
        self.btn_browse.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.btn_browse)
        form.addRow("Папка проекта:", path_layout)
        
        # Описание
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        self.desc_edit.setPlaceholderText("Краткое описание проекта (необязательно)")
        form.addRow("Описание:", self.desc_edit)
        
        layout.addLayout(form)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Заполняем поля при редактировании
        if edit_mode and project_data:
            self.name_edit.setText(project_data[1])
            self.desc_edit.setText(project_data[2])
            self.path_edit.setText(project_data[3])
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку проекта",
            str(Path.home()),
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.path_edit.setText(folder)
    
    def validate_and_accept(self):
        name = self.name_edit.text().strip()
        root_path = self.path_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название проекта не может быть пустым.")
            return
        
        if not root_path:
            QMessageBox.warning(self, "Ошибка", "Выберите папку проекта.")
            return
        
        if not Path(root_path).exists():
            QMessageBox.warning(self, "Ошибка", "Выбранная папка не существует.")
            return
        
        self.accept()
    
    def get_data(self):
        return (
            self.name_edit.text().strip(),
            self.desc_edit.toPlainText().strip(),
            self.path_edit.text().strip()
        )