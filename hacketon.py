import sys
import random
import string
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QListWidget, QLineEdit, QDialog, QFormLayout, QSpinBox, QCheckBox, 
    QMessageBox, QListWidgetItem, QHBoxLayout
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

PASSWORDS_FILE = "passwords.json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Password Manager")
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet("background-color: #1e2a34; color: white;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.title_label = QLabel("Secure Your Digital Worlds")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.start_button = QPushButton("Get Started")
        self.start_button.setStyleSheet("background-color: #4caf50; font-size: 18px; padding: 10px;")
        self.start_button.clicked.connect(self.show_password_list)
        self.layout.addWidget(self.start_button)

    def show_password_list(self):
        self.password_list_window = PasswordListWindow()
        self.password_list_window.show()
        self.close()

class PasswordListWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Your Passwords")
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet("background-color: #1e2a34; color: white;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.site_list_widget = QListWidget()
        self.layout.addWidget(self.site_list_widget)

        self.new_password_button = QPushButton("New Password")
        self.new_password_button.setStyleSheet("background-color: #4caf50; font-size: 18px; padding: 10px;")
        self.new_password_button.clicked.connect(self.show_new_password_dialog)
        self.layout.addWidget(self.new_password_button)

        self.passwords = {}
        self.load_passwords()

    def show_new_password_dialog(self):
        self.new_password_dialog = NewPasswordDialog(self)
        self.new_password_dialog.exec_()

    def add_password(self, site_name, password):
        if site_name in self.passwords:
            self.passwords[site_name].append(password)
        else:
            self.passwords[site_name] = [password]
        self.save_passwords()
        self.update_password_list()

    def load_passwords(self):
        if os.path.exists(PASSWORDS_FILE):
            with open(PASSWORDS_FILE, "r") as file:
                self.passwords = json.load(file)
        self.update_password_list()

    def save_passwords(self):
        with open(PASSWORDS_FILE, "w") as file:
            json.dump(self.passwords, file)

    def update_password_list(self):
        self.site_list_widget.clear()
        for site_name, passwords in self.passwords.items():
            for password in passwords:
                widget = QWidget()
                layout = QHBoxLayout()
                widget.setLayout(layout)

                password_label = QLineEdit(password)
                password_label.setEchoMode(QLineEdit.Password)
                password_label.setReadOnly(True)

                show_button = QPushButton("Show")
                show_button.setCheckable(True)
                show_button.toggled.connect(lambda checked, pw=password_label: self.toggle_password_visibility(checked, pw))

                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda _, sn=site_name, pw=password: self.delete_password(sn, pw))

                layout.addWidget(QLabel(f"{site_name}:"))
                layout.addWidget(password_label)
                layout.addWidget(show_button)
                layout.addWidget(delete_button)

                item = QListWidgetItem()
                item.setSizeHint(widget.sizeHint())
                self.site_list_widget.addItem(item)
                self.site_list_widget.setItemWidget(item, widget)

    def toggle_password_visibility(self, checked, password_label):
        if checked:
            password_label.setEchoMode(QLineEdit.Normal)
        else:
            password_label.setEchoMode(QLineEdit.Password)

    def delete_password(self, site_name, password):
        try:
            if site_name in self.passwords:
                if password in self.passwords[site_name]:
                    self.passwords[site_name].remove(password)
                    if not self.passwords[site_name]:
                        del self.passwords[site_name]
                    self.save_passwords()
                    self.update_password_list()
                else:
                    raise ValueError("Password not found")
            else:
                raise ValueError("Site not found")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Critical Error", f"An unexpected error occurred: {str(e)}")

class NewPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setWindowTitle("New Password")
        self.setGeometry(150, 150, 300, 300)
        self.setStyleSheet("background-color: #1e2a34; color: white;")

        layout = QFormLayout()
        self.setLayout(layout)

        self.site_name_input = QLineEdit()
        layout.addRow("Site Name:", self.site_name_input)

        self.length_spinbox = QSpinBox()
        self.length_spinbox.setValue(16)
        layout.addRow("Length:", self.length_spinbox)

        self.uppercase_checkbox = QCheckBox()
        layout.addRow("Include Uppercase:", self.uppercase_checkbox)

        self.numbers_checkbox = QCheckBox()
        layout.addRow("Include Numbers:", self.numbers_checkbox)

        self.symbols_checkbox = QCheckBox()
        layout.addRow("Include Symbols:", self.symbols_checkbox)

        self.generate_button = QPushButton("Generate Password")
        self.generate_button.setStyleSheet("background-color: #4caf50; padding: 10px;")
        self.generate_button.clicked.connect(self.generate_password)
        layout.addWidget(self.generate_button)

        self.password_output = QLineEdit()
        self.password_output.setReadOnly(True)
        layout.addWidget(self.password_output)

        self.save_button = QPushButton("Save Password")
        self.save_button.setStyleSheet("background-color: #2196f3; padding: 10px;")
        self.save_button.clicked.connect(self.save_password)
        layout.addWidget(self.save_button)

    def generate_password(self):
        length = self.length_spinbox.value()
        include_uppercase = self.uppercase_checkbox.isChecked()
        include_numbers = self.numbers_checkbox.isChecked()
        include_symbols = self.symbols_checkbox.isChecked()

        characters = string.ascii_lowercase
        if include_uppercase:
            characters += string.ascii_uppercase
        if include_numbers:
            characters += string.digits
        if include_symbols:
            characters += string.punctuation

        password = ''.join(random.choice(characters) for _ in range(length))
        self.password_output.setText(password)

    def save_password(self):
        site_name = self.site_name_input.text().strip()
        password = self.password_output.text().strip()

        if site_name and password:
            self.parent.add_password(site_name, password)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Site name and password cannot be empty.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
