from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QFrame, QPushButton, QLineEdit

from src.core.player import Player
from src.core.library_manager import LibraryManager
from src.ui.components.library_item import LibraryItem

class LibraryTab(QWidget):
    play_requested = Signal(list, int, bool)

    def __init__(self):
        super().__init__()
        self.manager = LibraryManager()
        self.all_songs = []
        self.current_song_list = []
        self.init_ui()
        self.load_library()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        lbl_header = QLabel("My Library")
        lbl_header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search saved songs...")
        self.search_bar.setFixedWidth(250)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #3B4252;
                color: white;
                border-radius: 15px;
                padding: 5px 15px;
                border: 1px solid #4C566A;
            }
            QLineEdit:focus { border: 1px solid #88C0D0; }
        """)
        self.search_bar.textChanged.connect(self.filter_library)

        # Rescan Button
        btn_rescan = QPushButton("↻")
        btn_rescan.setToolTip("Rescan Library")
        btn_rescan.setCursor(Qt.PointingHandCursor)
        btn_rescan.setFixedSize(30, 30)
        btn_rescan.setStyleSheet("""
            QPushButton { background-color: #3B4252; color: white; border-radius: 15px; border: 1px solid #4C566A; font-size: 16px; }
            QPushButton:hover { background-color: #434C5E; border-color: #88C0D0; }
        """)
        btn_rescan.clicked.connect(self.refresh_library)

        btn_play_all = QPushButton("▶ Play All")
        btn_play_all.setCursor(Qt.PointingHandCursor)
        btn_play_all.setStyleSheet("""
            QPushButton { background-color: #88C0D0; color: #2E3440; font-weight: bold; border-radius: 15px; padding: 5px 15px; }
            QPushButton:hover { background-color: #81A1C1; }
        """)
        btn_play_all.clicked.connect(self.play_all)

        btn_shuffle = QPushButton("🔀 Shuffle")
        btn_shuffle.setCursor(Qt.PointingHandCursor)
        btn_shuffle.setStyleSheet("""
            QPushButton { background-color: #3B4252; color: white; font-weight: bold; border-radius: 15px; padding: 5px 15px; border: 1px solid #4C566A; }
            QPushButton:hover { background-color: #434C5E; border-color: #88C0D0; }
        """)
        btn_shuffle.clicked.connect(self.shuffle_all)

        header_layout.addWidget(lbl_header)
        header_layout.addStretch()
        header_layout.addWidget(self.search_bar)
        header_layout.addWidget(btn_rescan)
        header_layout.addWidget(btn_play_all)
        header_layout.addWidget(btn_shuffle)
        layout.addLayout(header_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.list_layout.setSpacing(5)
        
        self.scroll.setWidget(self.list_container)
        layout.addWidget(self.scroll)

    def load_library(self):
        self.manager.library_changed.connect(self.on_library_loaded)
        self.manager.load_library()

    def refresh_library(self):
        self.manager.refresh_library()

    def on_library_loaded(self, songs):
        self.all_songs = songs
        self.filter_library(self.search_bar.text())

    def filter_library(self, text):
        query = text.lower().strip()
        
        if not query:
            filtered_songs = self.all_songs
        else:
            filtered_songs = [
                s for s in self.all_songs 
                if query in s.get('title', '').lower() 
                or query in s.get('artist', '').lower()
            ]
        
        self.populate_list(filtered_songs)

    def populate_list(self, songs):
        for i in range(self.list_layout.count()):
            child = self.list_layout.itemAt(i).widget()
            if child: child.deleteLater()

        self.current_song_list = songs
        
        if not songs:
            msg = "No songs found." if self.all_songs else "Library empty. Go download some!"
            self.list_layout.addWidget(QLabel(msg, alignment=Qt.AlignCenter))
            return

        for index, song in enumerate(songs):
            item = LibraryItem(song)
            item.play_clicked.connect(lambda s=song, idx=index: self.on_item_play(idx))
            self.list_layout.addWidget(item)
    
    def on_item_play(self, index):
        self.play_requested.emit(self.current_song_list, index, False)
    
    def play_all(self):
        if self.current_song_list:
            self.play_requested.emit(self.current_song_list, 0, False)

    def shuffle_all(self):
        if self.current_song_list:
            self.play_requested.emit(self.current_song_list, 0, True)

