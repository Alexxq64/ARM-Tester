# gui/login_window.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from db.database import Database

class LoginWindow(QDialog):
    def __init__(self, db_path="arm_testing.db"):
        super().__init__()
        self.db = Database(db_path)
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Логин")
        layout.addWidget(self.login_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.check_auth)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def check_auth(self):
        user = self.db.get_user(
            self.login_edit.text(),
            self.password_edit.text()
        )
        if user:
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")