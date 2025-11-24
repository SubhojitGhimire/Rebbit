from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QScrollArea, QFrame, QLabel, QMessageBox

from src.utils.config import Config
from src.ui.components.song_card import SongCard
from src.core.download_manager import DownloadManager
from src.core.downloader import SearchWorker, DownloadWorker

class SearchTab(QWidget):
    def __init__(self):
        super().__init__()
        self.active_downloads = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        search_layout = QHBoxLayout()
        
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Search Song or Paste YouTube Link...")
        self.input_search.setFixedHeight(45)
        self.input_search.setStyleSheet("""
            QLineEdit {
                background-color: #3B4252;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                border: 1px solid #4C566A;
            }
            QLineEdit:focus { border: 1px solid #88C0D0; }
        """)
        self.input_search.returnPressed.connect(self.start_search)
        
        self.btn_search = QPushButton("Search")
        self.btn_search.setFixedHeight(45)
        self.btn_search.setCursor(Qt.PointingHandCursor)
        self.btn_search.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: white;
                border-radius: 8px;
                padding: 0 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #81A1C1; }
        """)
        self.btn_search.clicked.connect(self.start_search)

        search_layout.addWidget(self.input_search)
        search_layout.addWidget(self.btn_search)
        layout.addLayout(search_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.results_container = QWidget()
        self.results_container.setStyleSheet("background: transparent;")
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setAlignment(Qt.AlignTop)
        self.results_layout.setSpacing(10)
        
        self.scroll.setWidget(self.results_container)
        layout.addWidget(self.scroll)
        
        self.lbl_loading = QLabel("Searching YouTube...", alignment=Qt.AlignCenter)
        self.lbl_loading.setStyleSheet("color: #88C0D0; font-size: 14px; font-style: italic;")
        self.lbl_loading.hide()
        layout.addWidget(self.lbl_loading)

    def start_search(self):
        query = self.input_search.text().strip()
        if not query:
            return

        for i in range(self.results_layout.count()):
            child = self.results_layout.itemAt(i).widget()
            if child: child.deleteLater()

        self.lbl_loading.show()
        self.btn_search.setEnabled(False)
        
        self.worker = SearchWorker(query)
        self.worker.finished.connect(self.handle_results)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def handle_results(self, results):
        self.lbl_loading.hide()
        self.btn_search.setEnabled(True)
        
        if not results:
            no_res = QLabel("No results found.")
            no_res.setStyleSheet("color: #BF616A; font-size: 16px;")
            self.results_layout.addWidget(no_res)
            return

        for video in results:
            card = SongCard(video)
            card.download_clicked.connect(self.start_download)
            self.results_layout.addWidget(card)

    def handle_error(self, error_msg):
        self.lbl_loading.hide()
        self.btn_search.setEnabled(True)
        print(f"Search Error: {error_msg}")

    def start_download(self, url, title):
        DownloadManager.instance().start_download(url, title)
        sender_card = self.sender()
        if sender_card and hasattr(sender_card, 'btn_download'):
            sender_card.update_status("Added to Queue")
            sender_card.btn_download.setEnabled(False)

