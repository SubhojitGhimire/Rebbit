from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget

from src.utils.config import Config
from src.core.player import RepeatMode
from src.ui.components.marquee_label import MarqueeLabel
from src.ui.components.custom_slider import CustomSlider

class NowPlayingBar(QFrame):
    play_clicked = Signal()
    next_clicked = Signal()
    prev_clicked = Signal()
    seek_requested = Signal(int)
    volume_changed = Signal(float)
    shuffle_toggled = Signal()
    repeat_toggled = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(90)
        self.setObjectName("NowPlayingBar") 
        self.setStyleSheet("""
            #NowPlayingBar {
                background-color: #1E1F22; 
                border-top: 1px solid #3E4045;
            }
            QLabel { border: none; background: transparent; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)

        self.lbl_art = QLabel()
        self.lbl_art.setFixedSize(60, 60)
        self.lbl_art.setStyleSheet("background-color: #333; border-radius: 6px;")
        self.lbl_art.setScaledContents(True)
        
        text_container = QWidget()
        text_container.setFixedWidth(200)
        text_container.setStyleSheet("background: transparent; border: none;")
        
        info_layout = QVBoxLayout(text_container)
        info_layout.setContentsMargins(0,0,0,0)
        info_layout.setAlignment(Qt.AlignVCenter)
        info_layout.setSpacing(2)
        
        self.lbl_title = MarqueeLabel("Select a song") 
        self.lbl_title.setStyleSheet("color: white; font-weight: bold; font-size: 14px; background: transparent;")
        
        self.lbl_artist = MarqueeLabel("") 
        self.lbl_artist.setStyleSheet("color: #88C0D0; font-size: 12px; background: transparent;")
        
        info_layout.addWidget(self.lbl_title)
        info_layout.addWidget(self.lbl_artist)

        layout.addWidget(self.lbl_art)
        layout.addWidget(text_container) 
        layout.addStretch(1)

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(5)
        
        btns_layout = QHBoxLayout()
        btns_layout.setAlignment(Qt.AlignCenter)
        btns_layout.setSpacing(15)
        
        self.btn_shuffle = self.create_btn("shuffle.svg", 20)
        self.btn_shuffle.clicked.connect(self.shuffle_toggled.emit)
        
        self.btn_prev = self.create_btn("previous.svg", 24)
        self.btn_prev.clicked.connect(self.prev_clicked.emit)
        
        self.btn_play = self.create_btn("play.svg", 38)
        self.btn_play.clicked.connect(self.play_clicked.emit)
        
        self.btn_next = self.create_btn("skip.svg", 24)
        self.btn_next.clicked.connect(self.next_clicked.emit)
        
        self.btn_repeat = self.create_btn("repeat.svg", 20)
        self.btn_repeat.clicked.connect(self.repeat_toggled.emit)
        
        btns_layout.addWidget(self.btn_shuffle)
        btns_layout.addWidget(self.btn_prev)
        btns_layout.addWidget(self.btn_play)
        btns_layout.addWidget(self.btn_next)
        btns_layout.addWidget(self.btn_repeat)
        
        self.seek_slider = CustomSlider(Qt.Horizontal)
        self.seek_slider.setFixedWidth(400)
        self.seek_slider.seek_request.connect(self.seek_requested.emit)

        center_layout.addLayout(btns_layout)
        center_layout.addWidget(self.seek_slider)
        
        layout.addLayout(center_layout)
        layout.addStretch(1)

        vol_layout = QHBoxLayout()
        vol_layout.setSpacing(10)
        lbl_vol = QLabel("Vol")
        lbl_vol.setStyleSheet("color: #88C0D0; font-weight: bold; background: transparent;")
        
        self.vol_slider = CustomSlider(Qt.Horizontal)
        self.vol_slider.setFixedWidth(100)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(70)
        self.vol_slider.seek_request.connect(lambda v: self.volume_changed.emit(v / 100.0))
        
        vol_layout.addWidget(lbl_vol)
        vol_layout.addWidget(self.vol_slider)
        layout.addLayout(vol_layout)
        
    def create_btn(self, icon, size):
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(QIcon(Config.get_icon_path(icon)))
        btn.setIconSize(QSize(size, size))
        btn.setStyleSheet("background: transparent; border: none;")
        return btn

    def update_info(self, song_data):
        self.seek_slider.setValue(0) 
        self.lbl_title.setText(song_data.get('title', 'Unknown'))
        self.lbl_artist.setText(song_data.get('artist', 'Unknown'))
        if song_data.get('cover_path'):
            self.lbl_art.setPixmap(QPixmap(song_data['cover_path']))
        else:
            self.lbl_art.setPixmap(QPixmap(Config.get_icon_path("default_vinyl.png")))

    def set_playing(self, is_playing):
        icon = "pause.svg" if is_playing else "play.svg"
        self.btn_play.setIcon(QIcon(Config.get_icon_path(icon)))

    def update_duration(self, duration):
        if duration > 0:
            self.seek_slider.setMaximum(duration)

    def update_progress(self, pos):
        if not self.seek_slider.is_dragging:
            self.seek_slider.setValue(pos)
    
    def update_shuffle_state(self, is_shuffle):
        color = "#88C0D0" if is_shuffle else "#FFFFFF"
        self.btn_shuffle.setStyleSheet(f"background: transparent; border: none; color: {color};")
        
    def update_repeat_state(self, mode):
        if mode == RepeatMode.NONE:
            self.btn_repeat.setToolTip("Repeat: Off")
            self.btn_repeat.setStyleSheet("background: transparent;")
        elif mode == RepeatMode.ALL:
            self.btn_repeat.setToolTip("Repeat: All")
            self.btn_repeat.setStyleSheet("background-color: rgba(136, 192, 208, 0.2); border-radius: 4px;")
        elif mode == RepeatMode.ONE:
            self.btn_repeat.setToolTip("Repeat: One")
            self.btn_repeat.setStyleSheet("background-color: rgba(136, 192, 208, 0.5); border-radius: 4px;")

