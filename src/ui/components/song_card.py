import requests
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame

class ImageLoader(QThread):
    loaded = Signal(QPixmap)
    def __init__(self, url):
        super().__init__()
        self.url = url
    def run(self):
        try:
            data = requests.get(self.url).content
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.loaded.emit(pixmap)
        except:
            pass

class SongCard(QFrame):
    download_clicked = Signal(str, str) 

    def __init__(self, video_data):
        super().__init__()
        self.video_data = video_data
        self.setFixedSize(700, 80)
        self.setStyleSheet("""
            SongCard {
                background-color: #2E3440;
                border-radius: 8px;
                border: 1px solid #3B4252;
            }
            SongCard:hover { border: 1px solid #88C0D0; }
            QLabel { border: none; }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(60, 60)
        self.thumb_label.setStyleSheet("background-color: #000; border-radius: 4px;")
        self.thumb_label.setScaledContents(True)
        layout.addWidget(self.thumb_label)
        
        thumbnails = video_data.get('thumbnails', [])
        if thumbnails:
            url = thumbnails[-1]['url'] if isinstance(thumbnails, list) else ""
            if url:
                self.loader = ImageLoader(url)
                self.loader.loaded.connect(self.thumb_label.setPixmap)
                self.loader.start()

        text_layout = QVBoxLayout()
        title = video_data.get('title', 'Unknown Title')
        uploader = video_data.get('uploader', 'Unknown Artist')
        is_playlist = video_data.get('is_playlist', False)
        
        if is_playlist:
            count = video_data.get('video_count', '?')
            badge_text = f" [PLAYLIST • {count} Tracks]"
            lbl_title = QLabel(title + badge_text)
            lbl_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #EBCB8B;")
        else:
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
            
        lbl_uploader = QLabel(uploader)
        lbl_uploader.setStyleSheet("color: #D8DEE9; font-size: 12px;")
        
        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_uploader)
        layout.addLayout(text_layout)
        layout.addStretch()

        btn_text = "Download All" if is_playlist else "Download"
        self.btn_download = QPushButton(btn_text)
        self.btn_download.setCursor(Qt.PointingHandCursor)
        self.btn_download.setFixedSize(110, 35)
        self.btn_download.setStyleSheet("""
            QPushButton {
                background-color: #88C0D0;
                color: #2E3440;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #81A1C1; }
            QPushButton:disabled { background-color: #4C566A; color: #D8DEE9; }
        """)
        self.btn_download.clicked.connect(self.on_download)
        layout.addWidget(self.btn_download)

    def on_download(self):
        self.btn_download.setText("Queued...")
        self.btn_download.setEnabled(False)
        url = self.video_data.get('webpage_url') or self.video_data.get('url')
        self.download_clicked.emit(url, self.video_data['title'])
    
    def update_status(self, text):
        self.btn_download.setText(text)

