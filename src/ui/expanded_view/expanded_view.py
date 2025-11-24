from PySide6.QtGui import QPixmap
from src.utils.config import Config
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame

from src.ui.expanded_view.queue_tab import QueueTab
from src.ui.expanded_view.search_tab import SearchTab
from src.ui.expanded_view.library_tab import LibraryTab
from src.ui.expanded_view.settings_tab import SettingsTab
from src.ui.components.now_playing_bar import NowPlayingBar
from src.ui.expanded_view.playlists_tab import PlaylistsTab

class ExpandedView(QWidget):
    minimize_requested = Signal()
    quit_requested = Signal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle(f"{Config.APP_NAME} Manager")
        self.resize(1000, 650) 
        self.setWindowFlags(Qt.Window)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setStyleSheet("background-color: #1E1F22; border-right: 1px solid #323438;")
        self.sidebar.setFixedWidth(240) 
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(15)

        container = QWidget()
        container.setStyleSheet("border: none; background: transparent;") 
        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)

        lbl_text = QLabel("Rebbit")
        lbl_text.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD7FA; border: none;")

        lbl_icon = QLabel()
        lbl_icon.setStyleSheet("border: none;")
        lbl_icon.setPixmap(QPixmap(Config.get_icon_path("logo.png")).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        h.addWidget(lbl_text)
        h.addWidget(lbl_icon)

        sidebar_layout.addWidget(container, alignment=Qt.AlignCenter)
        
        self.btn_search = self.create_sidebar_btn("Search and Download")
        self.btn_library = self.create_sidebar_btn("My Library")
        self.btn_playlists = self.create_sidebar_btn("Playlists")
        self.btn_queue = self.create_sidebar_btn("Download Queue")
        
        sidebar_layout.addWidget(self.btn_search)
        sidebar_layout.addWidget(self.btn_library)
        sidebar_layout.addWidget(self.btn_playlists)
        sidebar_layout.addWidget(self.btn_queue)
        sidebar_layout.addStretch()

        self.btn_minimize = self.create_sidebar_btn("Minimize to Widget")
        self.btn_minimize.clicked.connect(self.minimize_requested.emit)
        self.btn_minimize.setStyleSheet("color: #EBCB8B;") 
        self.btn_settings = self.create_sidebar_btn("Settings")
        self.btn_settings.setStyleSheet("color: #8DEB9E;")
        self.btn_quit = self.create_sidebar_btn("Quit")
        self.btn_quit.clicked.connect(self.quit_requested.emit)
        self.btn_quit.setStyleSheet("color: #BF616A;") 

        sidebar_layout.addWidget(self.btn_minimize)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addWidget(self.btn_quit)

        self.content_area = QFrame()
        self.content_area.setObjectName("ContentArea")
        self.content_area.setStyleSheet("background-color: #25262B;")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0,0,0,0)
        
        self.pages = QStackedWidget()
        
        self.search_tab = SearchTab()
        self.library_tab = LibraryTab()
        self.playlists_tab = PlaylistsTab()
        self.queue_tab = QueueTab()             
        self.settings_tab = SettingsTab(self.app) 
        
        self.pages.addWidget(self.search_tab)
        self.pages.addWidget(self.library_tab)
        self.pages.addWidget(self.playlists_tab)
        self.pages.addWidget(self.queue_tab)
        self.pages.addWidget(self.settings_tab)
        
        content_layout.addWidget(self.pages)

        self.player_bar = NowPlayingBar()
        content_layout.addWidget(self.player_bar)

        self.btn_search.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.btn_library.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.btn_playlists.clicked.connect(lambda: self.pages.setCurrentIndex(2))
        self.btn_queue.clicked.connect(lambda: self.pages.setCurrentIndex(3))
        self.btn_settings.clicked.connect(lambda: self.pages.setCurrentIndex(4))
        
        main_layout.addWidget(self.sidebar, 0) 
        main_layout.addWidget(self.content_area, 1)

    def create_sidebar_btn(self, text):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 15px;
                background-color: transparent;
                border: none;
                color: #D8DEE9;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2E3440;
                border-radius: 5px;
                color: #FFFFFF;
            }
            QPushButton:pressed { background-color: #3B4252; }
        """)
        return btn

