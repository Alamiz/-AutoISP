from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QComboBox, QTextEdit, QHBoxLayout, QCheckBox, QGroupBox
)
import sys
from core.runner import run_automation
from core.utils.logger import QTextEditLogger
import logging

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AutoISP Prototype")
        self.resize(450, 700)

        layout = QVBoxLayout()

        # Email
        self.email = QLineEdit()
        self.email.setText("tolik.last71@web.de")
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email)

        # Password
        self.password = QLineEdit()
        self.password.setText("huWyEVUiB")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password)

        # Provider
        self.provider = QComboBox()
        self.provider.addItems(["webde", "gmx"])
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

        # Proxy section (optional) - now in a group box
        proxy_group = QGroupBox("Proxy Settings (Optional)")
        proxy_layout = QVBoxLayout()
        
        self.enable_proxy = QCheckBox("Enable Proxy")
        self.enable_proxy.setChecked(True)  # Default enabled
        self.enable_proxy.stateChanged.connect(self.toggle_proxy_fields)
        proxy_layout.addWidget(self.enable_proxy)

        # Proxy type
        proxy_type_layout = QHBoxLayout()
        proxy_type_layout.addWidget(QLabel("Type:"))
        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["http", "https", "socks5"])
        proxy_type_layout.addWidget(self.proxy_type)
        proxy_type_layout.addStretch()
        proxy_layout.addLayout(proxy_type_layout)

        # Proxy host
        proxy_host_layout = QHBoxLayout()
        proxy_host_layout.addWidget(QLabel("Host:"))
        self.proxy_host = QLineEdit()
        self.proxy_host.setText("87.106.110.76")  # Default proxy
        self.proxy_host.setPlaceholderText("proxy.example.com or IP")
        proxy_host_layout.addWidget(self.proxy_host)
        proxy_layout.addLayout(proxy_host_layout)

        # Proxy port
        proxy_port_layout = QHBoxLayout()
        proxy_port_layout.addWidget(QLabel("Port:"))
        self.proxy_port = QLineEdit()
        self.proxy_port.setText("9119")  # Default port
        self.proxy_port.setPlaceholderText("8080")
        proxy_port_layout.addWidget(self.proxy_port)
        proxy_layout.addLayout(proxy_port_layout)

        # Proxy username (optional)
        proxy_user_layout = QHBoxLayout()
        proxy_user_layout.addWidget(QLabel("Username:"))
        self.proxy_username = QLineEdit()
        self.proxy_username.setText("auroproxy")  # Default username
        self.proxy_username.setPlaceholderText("Optional - leave empty if not needed")
        proxy_user_layout.addWidget(self.proxy_username)
        proxy_layout.addLayout(proxy_user_layout)

        # Proxy password (optional)
        proxy_pass_layout = QHBoxLayout()
        proxy_pass_layout.addWidget(QLabel("Password:"))
        self.proxy_password = QLineEdit()
        self.proxy_password.setText("auroraproxy9595")  # Default password
        self.proxy_password.setPlaceholderText("Optional - leave empty if not needed")
        self.proxy_password.setEchoMode(QLineEdit.Password)
        proxy_pass_layout.addWidget(self.proxy_password)
        proxy_layout.addLayout(proxy_pass_layout)

        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)

        # Initially disable proxy fields
        self.toggle_proxy_fields()

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

    def toggle_proxy_fields(self):
        """Enable/disable proxy fields based on checkbox"""
        enabled = self.enable_proxy.isChecked()
        self.proxy_type.setEnabled(enabled)
        self.proxy_host.setEnabled(enabled)
        self.proxy_port.setEnabled(enabled)
        self.proxy_username.setEnabled(enabled)
        self.proxy_password.setEnabled(enabled)

    def get_proxy_config(self):
        """Get proxy configuration if enabled - returns OLD format to match existing code"""
        if not self.enable_proxy.isChecked():
            return None
        
        host = self.proxy_host.text().strip()
        port = self.proxy_port.text().strip()
        
        if not host or not port:
            self.write_log("Warning: Proxy enabled but host or port is empty")
            return None
        
        # Return OLD format that your existing code expects
        proxy_config = {
            'type': self.proxy_type.currentText(),  # http, https, or socks5
            'host': host,
            'port': port
        }
        
        # Add authentication if provided
        username = self.proxy_username.text().strip()
        password = self.proxy_password.text().strip()
        
        if username and password:
            proxy_config['username'] = username
            proxy_config['password'] = password
        
        return proxy_config

    def run_authentication(self):
        email = self.email.text()
        password = self.password.text()
        provider = self.provider.currentText()
        device_type = self.device_type.currentText()
        proxy_config = self.get_proxy_config()

        if not email:
            self.write_log("Please enter an email.")
            return

        self.write_log(f"Starting authentication for {email} on {provider}...")
        self.write_log(f"Device type: {device_type}")
        
        if proxy_config:
            proxy_info = f"{proxy_config['protocol']}://{proxy_config['host']}:{proxy_config['port']}"
            if 'username' in proxy_config:
                proxy_info = f"{proxy_config['protocol']}://{proxy_config['username']}:***@{proxy_config['host']}:{proxy_config['port']}"
            self.write_log(f"Using proxy: {proxy_info}")

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