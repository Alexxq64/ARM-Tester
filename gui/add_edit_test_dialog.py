from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QCheckBox, QDialogButtonBox, QMessageBox, QPushButton, QHBoxLayout, QFileDialog
from pathlib import Path

class AddEditTestDialog(QDialog):
    def __init__(self, parent=None, edit_mode=False, test_data=None):
        super().__init__(parent)
        self.edit_mode = edit_mode
        self.test_data = test_data
        self.setWindowTitle("Редактировать тест" if edit_mode else "Добавить тест")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.group_edit = QLineEdit()
        
        # Поле пути с кнопкой обзора
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.browse_btn = QPushButton("Обзор...")
        self.browse_btn.clicked.connect(self.browse_file)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        
        self.active_check = QCheckBox()
        self.active_check.setChecked(True)

        form.addRow("Название:", self.name_edit)
        form.addRow("Группа:", self.group_edit)
        form.addRow("Путь к тесту:", path_layout)
        form.addRow("Активен:", self.active_check)

        layout.addLayout(form)

        if edit_mode and test_data:
            self.name_edit.setText(test_data.get("name", ""))
            self.group_edit.setText(test_data.get("group_name", ""))
            self.path_edit.setText(test_data.get("test_path", ""))
            self.active_check.setChecked(test_data.get("is_active", 1) == 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл с тестом", 
            str(Path.home()), 
            "Python files (*.py);;All files (*)"
        )
        if file_path:
            self.path_edit.setText(file_path)

    def get_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "group_name": self.group_edit.text().strip(),
            "test_path": self.path_edit.text().strip(),
            "is_active": 1 if self.active_check.isChecked() else 0
        }

    def accept(self):
        data = self.get_data()
        if not data["name"]:
            QMessageBox.warning(self, "Ошибка", "Название теста не может быть пустым.")
            return
        if not data["test_path"]:
            QMessageBox.warning(self, "Ошибка", "Путь к тесту не может быть пустым.")
            return
        super().accept()