import sys
from PySide6.QtGui import QIcon, QPixmap, QAction
from PySide6.QtCore import Qt, QSize, Signal, QPoint
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFrame, QLabel, QMenu

from src.utils.config import Config
from src.ui.components.custom_slider import CustomSlider
from src.ui.components.marquee_label import MarqueeLabel 

class CollapsedView(QWidget):
    expand_requested = Signal()
    quit_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle(Config.APP_NAME)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.old_pos = None
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(360, 85) 

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.frame = QFrame()
        self.frame.setObjectName("CollapsedWidgetFrame")
        
        frame_main_layout = QVBoxLayout(self.frame)
        frame_main_layout.setContentsMargins(10, 5, 10, 5)
        frame_main_layout.setSpacing(5)
        
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.album_art = QLabel()
        self.album_art.setFixedSize(40, 40)
        default_art_path = Config.get_icon_path("default_vinyl.png")
        self.album_art.setPixmap(QPixmap(default_art_path).scaled(40, 40, Qt.KeepAspectRatio))
        self.album_art.setStyleSheet("background-color: #444; border-radius: 4px;")
        top_row.addWidget(self.album_art)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        text_layout.setAlignment(Qt.AlignVCenter)

        self.lbl_title = MarqueeLabel("No Song Selected") 
        self.lbl_title.setObjectName("SongTitle")
        self.lbl_title.setFixedHeight(20) 
        
        self.lbl_artist = MarqueeLabel("Waiting for music...") 
        self.lbl_artist.setObjectName("ArtistName")
        self.lbl_artist.setFixedHeight(15)

        text_layout.addWidget(self.lbl_title)
        text_layout.addWidget(self.lbl_artist)
        
        text_container = QWidget()
        text_container.setLayout(text_layout)
        text_container.setFixedWidth(180) 
        
        top_row.addWidget(text_container)
        top_row.addStretch() 

        self.btn_prev = self.create_nav_button("previous.svg", "Prev")
        self.btn_prev.setLayoutDirection(Qt.RightToLeft)
        self.btn_play = self.create_nav_button("play.svg", "Play")
        self.btn_next = self.create_nav_button("skip.svg", "Next")

        top_row.addWidget(self.btn_prev)
        top_row.addWidget(self.btn_play)
        top_row.addWidget(self.btn_next)

        frame_main_layout.addLayout(top_row)

        self.slider = CustomSlider()
        self.slider.setFixedHeight(10)
        frame_main_layout.addWidget(self.slider)

        layout.addWidget(self.frame)

    def create_nav_button(self, icon_name, tooltip):
        btn = QPushButton()
        btn.setFixedSize(32, 32)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        icon_path = Config.get_icon_path(icon_name)
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(16, 16))
        return btn

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def show_context_menu(self, pos):
        menu = QMenu(self)
        expand_action = QAction("Expand Widget", self)
        expand_action.triggered.connect(lambda: self.expand_requested.emit())
        settings_action = QAction("Settings", self)
        quit_action = QAction("Quit Rebbit", self)
        quit_action.triggered.connect(lambda: self.quit_requested.emit())
        menu.addAction(expand_action)
        menu.addSeparator()
        menu.addAction(settings_action)
        menu.addAction(quit_action)
        menu.exec(pos)

    def update_song_info(self, song_data):
        self.slider.setValue(0)
        self.lbl_title.setText(song_data.get('title', 'Unknown Title'))
        self.lbl_artist.setText(song_data.get('artist', 'Unknown Artist'))
        
        cover_path = song_data.get('cover_path')
        if cover_path:
            pixmap = QPixmap(cover_path)
            if not pixmap.isNull():
                self.album_art.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
        
        default_art_path = Config.get_icon_path("default_vinyl.png")
        self.album_art.setPixmap(QPixmap(default_art_path).scaled(40, 40, Qt.KeepAspectRatio))

    def set_playing_state(self, is_playing):
        icon_name = "pause.svg" if is_playing else "play.svg"
        self.btn_play.setIcon(QIcon(Config.get_icon_path(icon_name)))

    def update_duration(self, duration):
        if duration > 0:
            self.slider.setMaximum(duration)
        
    def update_position(self, position):
        if not self.slider.is_dragging:
            self.slider.setValue(position)

