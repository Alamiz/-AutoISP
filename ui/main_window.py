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
        self.resize(400, 600)  # Make the window bigger

        layout = QVBoxLayout()

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.provider = QComboBox()
        self.provider.addItems(["gmx", "webde"])

        # Proxy section
        proxy_layout = QVBoxLayout()
        proxy_label = QLabel("Proxy Settings (Optional)")
        
        # Enable proxy checkbox
        self.enable_proxy = QCheckBox("Enable Proxy")
        self.enable_proxy.setChecked(False)
        
        # Proxy type
        proxy_type_layout = QHBoxLayout()
        proxy_type_layout.addWidget(QLabel("Type:"))
        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["http", "https", "socks5"])
        proxy_type_layout.addWidget(self.proxy_type)
        proxy_type_layout.addStretch()
        
        # Proxy host and port
        proxy_host_layout = QHBoxLayout()
        proxy_host_layout.addWidget(QLabel("Host:"))
        self.proxy_host = QLineEdit()
        self.proxy_host.setPlaceholderText("proxy.example.com")
        proxy_host_layout.addWidget(self.proxy_host)
        
        proxy_port_layout = QHBoxLayout()
        proxy_port_layout.addWidget(QLabel("Port:"))
        self.proxy_port = QLineEdit()
        self.proxy_port.setPlaceholderText("8080")
        proxy_port_layout.addWidget(self.proxy_port)
        
        # Proxy authentication
        proxy_auth_layout = QHBoxLayout()
        proxy_auth_layout.addWidget(QLabel("Username:"))
        self.proxy_username = QLineEdit()
        self.proxy_username.setPlaceholderText("Optional")
        proxy_auth_layout.addWidget(self.proxy_username)
        
        proxy_pass_layout = QHBoxLayout()
        proxy_pass_layout.addWidget(QLabel("Password:"))
        self.proxy_password = QLineEdit()
        self.proxy_password.setPlaceholderText("Optional")
        self.proxy_password.setEchoMode(QLineEdit.Password)
        proxy_pass_layout.addWidget(self.proxy_password)

        # Add proxy widgets to proxy layout
        proxy_layout.addWidget(proxy_label)
        proxy_layout.addWidget(self.enable_proxy)
        proxy_layout.addLayout(proxy_type_layout)
        proxy_layout.addLayout(proxy_host_layout)
        proxy_layout.addLayout(proxy_port_layout)
        proxy_layout.addLayout(proxy_auth_layout)
        proxy_layout.addLayout(proxy_pass_layout)

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
        self.email.setText("maxtaagva@gmx.de")

        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password)
        self.password.setText("7QktmVDQxJd")

        layout.addWidget(QLabel("Provider"))
        layout.addWidget(self.provider)

        # Add proxy section
        layout.addLayout(proxy_layout)

        layout.addWidget(self.btn_login)

        layout.addWidget(QLabel("Logs"))
        layout.addWidget(self.log)

        self.setLayout(layout)

    def write_log(self, text):
        self.log.append(text)

    def get_proxy_config(self):
        """Get proxy configuration from form inputs"""
        if not self.enable_proxy.isChecked():
            return None
            
        proxy_config = {
            'type': self.proxy_type.currentText(),
            'host': self.proxy_host.text(),
            'port': self.proxy_port.text()
        }
        
        # Add authentication if provided
        if self.proxy_username.text() and self.proxy_password.text():
            proxy_config['username'] = self.proxy_username.text()
            proxy_config['password'] = self.proxy_password.text()
            
        return proxy_config

    def run_authentication(self):
        email = self.email.text()
        password = self.password.text()
        provider = self.provider.currentText()  # 'gmx' or 'webde'
        proxy_config = self.get_proxy_config()

        if not email:
            self.write_log("Please enter an email.")
            return

        self.write_log(f"Starting authentication for {email} on {provider}...")
        if proxy_config:
            self.write_log(f"Using proxy: {proxy_config['type']}://{proxy_config['host']}:{proxy_config['port']}")

        # You'll need to update run_automation function to accept proxy_config parameter
        run_automation(email, password, provider, "authenticate", proxy_config=proxy_config)


def run_ui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())