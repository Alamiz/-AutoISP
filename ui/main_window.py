from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QComboBox, QTextEdit
)
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AutoISP Prototype")
        layout = QVBoxLayout()

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.provider = QComboBox()
        self.provider.addItems(["gmx", "webde"])

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.btn_profile = QPushButton("Create Profile")
        self.btn_login = QPushButton("Login")

        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email)

        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password)

        layout.addWidget(QLabel("Provider"))
        layout.addWidget(self.provider)

        layout.addWidget(self.btn_profile)
        layout.addWidget(self.btn_login)

        layout.addWidget(QLabel("Logs"))
        layout.addWidget(self.log)

        self.setLayout(layout)

    def write_log(self, text):
        self.log.append(text)


def run_ui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
