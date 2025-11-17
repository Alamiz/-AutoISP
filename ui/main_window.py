from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QComboBox, QTextEdit
)
import sys
from core.runner import run_automation
from core.utils import QTextEditLogger
import logging

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AutoISP Prototype")
        self.resize(400, 600)  # Make the window bigger

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

        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.run_authentication)

        # Create logger
        self.logger = logging.getLogger("autoisp")
        self.logger.setLevel(logging.INFO)

        # Create handler for the QTextEdit
        text_edit_handler = QTextEditLogger(self.log)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        text_edit_handler.setFormatter(formatter)

        self.logger.addHandler(text_edit_handler)

        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email)

        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password)

        layout.addWidget(QLabel("Provider"))
        layout.addWidget(self.provider)

        layout.addWidget(self.btn_login)

        layout.addWidget(QLabel("Logs"))
        layout.addWidget(self.log)

        self.setLayout(layout)

    def write_log(self, text):
        self.log.append(text)

    def run_authentication(self):
        email = self.email.text()
        provider = self.provider.currentText()  # 'gmx' or 'webde'

        if not email:
            self.write_log("Please enter an email.")
            return

        self.write_log(f"Starting authentication for {email} on {provider}...")

        run_automation(email, provider, "authenticate")


def run_ui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

