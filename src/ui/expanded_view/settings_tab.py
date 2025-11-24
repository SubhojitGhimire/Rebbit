import re
import requests
from PySide6.QtCore import Qt, QObject, Signal, QThread
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QMessageBox

from src.utils.config import Config

class UpdateChecker(QObject):
    finished = Signal(str, bool)

    def run(self):
        try:
            local_version = Config.VERSION
            url = Config.get_update_url()
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            remote_content = response.text
            remote_version = self._parse_version(remote_content)

            if not remote_version:
                self.finished.emit("Could not determine remote version from GitHub.", False)
            elif remote_version == local_version:
                self.finished.emit(f"You are up to date! (Version {local_version})", False)
            else:
                self.finished.emit(f"A new version {remote_version} is available!\nCurrent: {local_version}", True)

        except requests.exceptions.RequestException:
            self.finished.emit("Error: Could not connect to GitHub to check for updates.", False)
        except Exception as e:
            self.finished.emit(f"An unexpected error occurred: {str(e)}", False)

    def _parse_version(self, content):
        match = re.search(r"Rebbit-(v[\d\.]+)", content, re.IGNORECASE)
        if not match:
            match = re.search(r"Version: (v[\d\.]+)", content, re.IGNORECASE)
        
        return match.group(1) if match else None

class SettingsTab(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app 
        self.update_thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        lbl_header = QLabel("Settings")
        lbl_header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(lbl_header)
        
        self.add_section_header(layout, "Appearance")
        
        theme_layout = QHBoxLayout()
        lbl_theme = QLabel("App Theme")
        lbl_theme.setStyleSheet("color: #D8DEE9; font-size: 14px;")
        
        btn_dark = QPushButton("Dark Mode")
        btn_dark.setCheckable(True)
        btn_dark.setChecked(True) 
        btn_dark.clicked.connect(lambda: self.set_theme("dark_theme.css"))
        self.style_btn(btn_dark)

        btn_light = QPushButton("Light Mode")
        btn_light.setCheckable(True)
        btn_light.clicked.connect(lambda: self.set_theme("light_theme.css"))
        self.style_btn(btn_light)
        
        btn_transparent = QPushButton("Transparent")
        btn_transparent.setCheckable(True)
        btn_transparent.clicked.connect(lambda: self.set_theme("transparent.css"))
        self.style_btn(btn_transparent)
        
        self.btn_group = [btn_dark, btn_light, btn_transparent]
        btn_dark.clicked.connect(lambda: self.update_toggles(btn_dark))
        btn_light.clicked.connect(lambda: self.update_toggles(btn_light))
        btn_transparent.clicked.connect(lambda: self.update_toggles(btn_transparent))

        theme_layout.addWidget(lbl_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(btn_dark)
        theme_layout.addWidget(btn_light)
        theme_layout.addWidget(btn_transparent)
        layout.addLayout(theme_layout)

        self.add_section_header(layout, "About Rebbit")
        
        info_text = (
            f"<b>Rebbit Music Player</b><br>"
            f"Version: {Config.VERSION}<br>"
            f"Developed by: Subhojit Ghimire<br>"
            f"Powered by: yt-dlp, PySide6, Mutagen"
        )
        lbl_info = QLabel(info_text)
        lbl_info.setStyleSheet("color: #D8DEE9; font-size: 13px; line-height: 1.4;")
        lbl_info.setTextFormat(Qt.RichText)
        layout.addWidget(lbl_info)
        
        self.btn_update = QPushButton("Check for Updates")
        self.style_btn(self.btn_update)
        self.btn_update.clicked.connect(self.check_updates)
        layout.addWidget(self.btn_update, alignment=Qt.AlignLeft)
        
        layout.addStretch()

    def add_section_header(self, layout, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #88C0D0; font-weight: bold; font-size: 16px; margin-top: 10px;")
        layout.addWidget(lbl)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #4C566A;")
        layout.addWidget(line)

    def style_btn(self, btn):
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(35)
        btn.setFixedWidth(140)
        btn.setStyleSheet("""
            QPushButton { background-color: #3B4252; color: white; border-radius: 4px; border: 1px solid #4C566A; }
            QPushButton:hover { background-color: #4C566A; }
            QPushButton:checked { background-color: #88C0D0; color: #2E3440; border: 1px solid #88C0D0; }
            QPushButton:disabled { background-color: #2E3440; color: #666; border: 1px solid #333; }
        """)

    def update_toggles(self, active_btn):
        for btn in self.btn_group:
            btn.setChecked(btn == active_btn)

    def set_theme(self, theme_file):
        path = Config.get_style_path(theme_file)
        try:
            with open(path, "r") as f:
                self.app.setStyleSheet(f.read())
        except:
            print(f"Could not load theme {path}")

    def check_updates(self):
        self.btn_update.setText("Checking...")
        self.btn_update.setEnabled(False)
        
        self.update_thread = QThread()
        self.update_worker = UpdateChecker()
        self.update_worker.moveToThread(self.update_thread)
        
        self.update_worker.finished.connect(self.on_update_checked)
        self.update_thread.started.connect(self.update_worker.run)
        
        self.update_worker.finished.connect(self.update_thread.quit)
        self.update_worker.finished.connect(self.update_worker.deleteLater)
        self.update_thread.finished.connect(self.update_thread.deleteLater)
        
        self.update_thread.start()
        
    def on_update_checked(self, message, is_available):
        self.btn_update.setText("Check for Updates")
        self.btn_update.setEnabled(True)
        
        if is_available:
            QMessageBox.information(self, "Update Available", message)
            # import webbrowser
            # webbrowser.open(f"https://github.com/{Config.GITHUB_USERNAME}/{Config.GITHUB_REPO}")
        else:
            QMessageBox.information(self, "Rebbit Updater", message)

