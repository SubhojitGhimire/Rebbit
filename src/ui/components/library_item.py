from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame

from src.utils.config import Config
from src.ui.context_menus import SongContextMenu

class LibraryItem(QFrame):
    play_clicked = Signal(dict)

    def __init__(self, song_data):
        super().__init__()
        self.song_data = song_data
        self.setFixedHeight(60)
        self.setStyleSheet("""
            LibraryItem {
                background-color: transparent;
                border-radius: 6px;
            }
            LibraryItem:hover {
                background-color: #2E3440;
            }
            QLabel { border: none; color: #D8DEE9; }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)

        self.thumb = QLabel()
        self.thumb.setFixedSize(50, 50)
        self.thumb.setStyleSheet("background-color: #444; border-radius: 4px;")
        self.thumb.setScaledContents(True)
        
        if song_data.get('cover_path'):
            pix = QPixmap(song_data['cover_path'])
            if not pix.isNull():
                self.thumb.setPixmap(pix)
        
        layout.addWidget(self.thumb)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setAlignment(Qt.AlignVCenter)
        
        lbl_title = QLabel(song_data.get('title', 'Unknown'))
        lbl_title.setStyleSheet("font-weight: bold; font-size: 13px; color: white;")
        
        lbl_artist = QLabel(song_data.get('artist', 'Unknown Artist'))
        lbl_artist.setStyleSheet("font-size: 11px; color: #88C0D0;")
        
        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_artist)
        layout.addLayout(text_layout, stretch=1)

        duration = song_data.get('duration', 0)
        mins, secs = divmod(duration, 60)
        lbl_dur = QLabel(f"{mins}:{secs:02d}")
        lbl_dur.setStyleSheet("color: #666;")
        layout.addWidget(lbl_dur)

        self.btn_play = QPushButton()
        self.btn_play.setFixedSize(30, 30)
        self.btn_play.setCursor(Qt.PointingHandCursor)
        self.btn_play.setIcon(QIcon(Config.get_icon_path("play.svg")))
        self.btn_play.setStyleSheet("background: transparent; border: none;")
        self.btn_play.clicked.connect(self.on_play)
        
        layout.addWidget(self.btn_play)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        global_pos = self.mapToGlobal(pos)
        SongContextMenu.show(self, self.song_data, global_pos)
    
    def on_play(self):
        self.play_clicked.emit(self.song_data)

