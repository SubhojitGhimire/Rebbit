from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea

from src.core.download_manager import DownloadManager
from src.ui.components.download_item import DownloadItem

class QueueTab(QWidget):
    def __init__(self):
        super().__init__()
        self.download_manager = DownloadManager.instance()
        self.init_ui()
        self.download_manager.task_added.connect(self.add_download_item)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_header = QLabel("Download Queue")
        lbl_header.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 10px;")
        layout.addWidget(lbl_header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        
        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.list_layout.setSpacing(10)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self.lbl_empty = QLabel("No active downloads.")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.lbl_empty.setStyleSheet("color: #666; font-size: 14px;")
        self.list_layout.addWidget(self.lbl_empty)

    def add_download_item(self, worker):
        if self.lbl_empty.isVisible():
            self.lbl_empty.hide()
            
        item = DownloadItem(worker)
        self.list_layout.insertWidget(0, item)

