from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QComboBox, QTextEdit, QHBoxLayout, QCheckBox
)
import sys
from core.runner import run_automation
from core.utils.logger import QTextEditLogger
import logging

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AutoISP Prototype")
        self.resize(400, 600)

        layout = QVBoxLayout()

        # Email
        self.email = QLineEdit()
        self.email.setText("maxtaagva@gmx.de")
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email)

        # Password
        self.password = QLineEdit()
        self.password.setText("7QktmVDQxJd")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password)

        # Provider
        self.provider = QComboBox()
        self.provider.addItems(["gmx", "webde"])
        layout.addWidget(QLabel("Provider"))
        layout.addWidget(self.provider)

        # Device Type
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device Type:"))
        self.device_type = QComboBox()
        self.device_type.addItems(["desktop", "mobile"])
        device_layout.addWidget(self.device_type)
        device_layout.addStretch()
        layout.addLayout(device_layout)

        # Proxy section (optional)
        proxy_layout = QVBoxLayout()
        self.enable_proxy = QCheckBox("Enable Proxy")
        self.enable_proxy.setChecked(False)
        proxy_layout.addWidget(self.enable_proxy)

        proxy_host_layout = QHBoxLayout()
        proxy_host_layout.addWidget(QLabel("Host:"))
        self.proxy_host = QLineEdit()
        self.proxy_host.setPlaceholderText("proxy.example.com")
        proxy_host_layout.addWidget(self.proxy_host)
        proxy_layout.addLayout(proxy_host_layout)

        proxy_port_layout = QHBoxLayout()
        proxy_port_layout.addWidget(QLabel("Port:"))
        self.proxy_port = QLineEdit()
        self.proxy_port.setPlaceholderText("8080")
        proxy_port_layout.addWidget(self.proxy_port)
        proxy_layout.addLayout(proxy_port_layout)

        layout.addWidget(QLabel("Proxy Settings (Optional)"))
        layout.addLayout(proxy_layout)

        # Login button
        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.run_authentication)
        layout.addWidget(self.btn_login)

        # Logs
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(QLabel("Logs"))
        layout.addWidget(self.log)

        # Logger setup
        self.logger = logging.getLogger("autoisp")
        self.logger.setLevel(logging.INFO)
        text_edit_handler = QTextEditLogger(self.log)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        text_edit_handler.setFormatter(formatter)
        self.logger.addHandler(text_edit_handler)

        self.setLayout(layout)

    def get_proxy_config(self):
        """Get proxy configuration if enabled"""
        if not self.enable_proxy.isChecked():
            return None
            
        proxy_config = {
            'type': 'http',  # Default to HTTP
            'host': self.proxy_host.text(),
            'port': self.proxy_port.text()
        }
        
        return proxy_config

    def run_authentication(self):
        email = self.email.text()
        password = self.password.text()
        provider = self.provider.currentText()
        device_type = self.device_type.currentText()  # "desktop" or "mobile"
        proxy_config = self.get_proxy_config()

        if not email:
            self.write_log("Please enter an email.")
            return

        self.write_log(f"Starting authentication for {email} on {provider}...")
        self.write_log(f"Device type: {device_type}")
        
        if proxy_config:
            self.write_log(f"Using proxy: {proxy_config['host']}:{proxy_config['port']}")

        # Pass device_type to run_automation
        run_automation(email, password, provider, "authenticate", 
                      proxy_config=proxy_config, device_type=device_type)

    def write_log(self, text):
        self.log.append(text)

def run_ui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())