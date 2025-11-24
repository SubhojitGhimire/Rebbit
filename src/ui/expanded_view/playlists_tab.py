from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QLabel, QFrame, QGridLayout, QInputDialog, QMenu, QMessageBox

from src.utils.config import Config
from src.utils.events import global_event_bus
from src.database.db_manager import DBManager
from src.ui.components.library_item import LibraryItem

class PlaylistsTab(QWidget):
    play_requested = Signal(list, int, bool)

    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.current_playlist_id = None
        self.init_ui()
        
        global_event_bus.playlists_updated.connect(self.load_playlists)
        global_event_bus.playlist_content_changed.connect(self.on_playlist_content_changed)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        header = QHBoxLayout()
        self.lbl_title = QLabel("My Playlists")
        self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        
        self.btn_back = QPushButton("← Back")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setStyleSheet("background-color: #3B4252; color: white; border-radius: 4px; padding: 5px 10px;")
        self.btn_back.clicked.connect(self.show_overview)
        self.btn_back.hide()

        self.btn_new = QPushButton("+ New Playlist")
        self.btn_new.setCursor(Qt.PointingHandCursor)
        self.btn_new.setStyleSheet("background-color: #88C0D0; color: #2E3440; font-weight: bold; border-radius: 4px; padding: 5px 10px;")
        self.btn_new.clicked.connect(self.create_playlist_dialog)

        header.addWidget(self.btn_back)
        header.addWidget(self.lbl_title)
        header.addStretch()
        header.addWidget(self.btn_new)
        self.main_layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        self.main_layout.addWidget(self.scroll)

        self.overview_widget = QWidget()
        self.overview_widget.setStyleSheet("background: transparent;")
        self.overview_layout = QGridLayout(self.overview_widget)
        self.overview_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.overview_layout.setSpacing(20)

        self.details_widget = QWidget()
        self.details_widget.setStyleSheet("background: transparent;")
        self.details_layout = QVBoxLayout(self.details_widget)
        self.details_layout.setAlignment(Qt.AlignTop)
        self.details_layout.setSpacing(5)

        self.show_overview()

    def load_playlists(self):
        for i in range(self.overview_layout.count()):
            item = self.overview_layout.itemAt(i).widget()
            if item: item.deleteLater()

        playlists = self.db.get_playlists()
        
        row, col = 0, 0
        for pl in playlists:
            card = self.create_playlist_card(pl)
            self.overview_layout.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def create_playlist_card(self, pl_data):
        card = QFrame()
        card.setFixedSize(160, 140)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet("""
            QFrame {
                background-color: #2E3440;
                border-radius: 10px;
                border: 1px solid #434C5E;
            }
            QFrame:hover {
                background-color: #3B4252;
                border: 1px solid #88C0D0;
            }
            QLabel { border: none; background: transparent; }
        """)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel() 
        pix = QPixmap(Config.get_icon_path("default_vinyl.png"))
        icon_lbl.setPixmap(pix.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_lbl.setAlignment(Qt.AlignCenter)
        
        name_lbl = QLabel(pl_data['name'])
        name_lbl.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        name_lbl.setWordWrap(True)
        name_lbl.setAlignment(Qt.AlignCenter)
        
        count_lbl = QLabel(f"{pl_data['song_count']} Songs")
        count_lbl.setStyleSheet("color: #D8DEE9; font-size: 12px;")
        
        layout.addWidget(icon_lbl, alignment=Qt.AlignCenter)
        layout.addWidget(name_lbl, alignment=Qt.AlignCenter)
        layout.addWidget(count_lbl, alignment=Qt.AlignCenter)

        card.mousePressEvent = lambda e: self.handle_card_click(e, pl_data)
        return card

    def handle_card_click(self, event, pl_data):
        if event.button() == Qt.LeftButton:
            self.open_playlist(pl_data)
        elif event.button() == Qt.RightButton:
            self.show_playlist_context_menu(pl_data, event.globalPos())

    def show_playlist_context_menu(self, pl_data, pos):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background-color: #25262B; border: 1px solid #3E4045; padding: 5px; color: white; }
            QMenu::item { padding: 5px 20px; }
            QMenu::item:selected { background-color: #88C0D0; color: black; }
        """)
        
        menu.addAction("Open").triggered.connect(lambda: self.open_playlist(pl_data))
        menu.addAction("Rename").triggered.connect(lambda: self.rename_playlist_dialog(pl_data))
        menu.addSeparator()
        
        del_action = menu.addAction("Delete")
        del_action.triggered.connect(lambda: self.delete_playlist(pl_data))
        
        menu.exec(pos)

    def create_playlist_dialog(self):
        name, ok = QInputDialog.getText(self, "New Playlist", "Name:")
        if ok and name:
            if self.db.create_playlist(name):
                global_event_bus.playlists_updated.emit()
            else:
                QMessageBox.warning(self, "Error", "Playlist already exists.")

    def rename_playlist_dialog(self, pl_data):
        name, ok = QInputDialog.getText(self, "Rename Playlist", "New Name:", text=pl_data['name'])
        if ok and name:
            if self.db.rename_playlist(pl_data['id'], name):
                global_event_bus.playlists_updated.emit()
            else:
                QMessageBox.warning(self, "Error", "Name already taken.")

    def delete_playlist(self, pl_data):
        confirm = QMessageBox.question(self, "Delete Playlist", f"Are you sure you want to delete '{pl_data['name']}'?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.db.delete_playlist(pl_data['id'])
            if self.current_playlist_id == pl_data['id']:
                self.show_overview()
            else:
                global_event_bus.playlists_updated.emit()

    def show_overview(self):
        self.current_playlist_id = None
        self.lbl_title.setText("My Playlists")
        self.btn_back.hide()
        self.btn_new.show()
        
        self.scroll.takeWidget() 
        self.scroll.setWidget(self.overview_widget)
        
        self.load_playlists()

    def open_playlist(self, pl_data):
        self.current_playlist_id = pl_data['id']
        self.lbl_title.setText(pl_data['name'])
        self.btn_back.show()
        self.btn_new.hide()
        
        self.load_playlist_songs(pl_data['id'])
        
        self.scroll.takeWidget()
        self.scroll.setWidget(self.details_widget)

    def on_playlist_content_changed(self, playlist_id):
        if self.current_playlist_id == playlist_id:
            self.load_playlist_songs(playlist_id)

    def load_playlist_songs(self, playlist_id):
        for i in range(self.details_layout.count()):
            item = self.details_layout.itemAt(i).widget()
            if item: item.deleteLater()

        songs = self.db.get_playlist_songs(playlist_id)
        
        if not songs:
            self.details_layout.addWidget(QLabel("Empty Playlist. Right click songs in Library to add here.", alignment=Qt.AlignCenter))
            return
            
        self.current_song_list = songs
        for idx, song in enumerate(songs):
            item = LibraryItem(song)
            
            item.customContextMenuRequested.disconnect() 
            item.customContextMenuRequested.connect(lambda pos, s=song, w=item: self.show_song_context_menu(pos, s, w))
            
            item.play_clicked.connect(lambda s=song, i=idx: self.play_requested.emit(self.current_song_list, i, False))
            self.details_layout.addWidget(item)

    def show_song_context_menu(self, pos, song_data, item_widget):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background-color: #25262B; border: 1px solid #3E4045; padding: 5px; color: white; }
            QMenu::item { padding: 5px 20px; }
            QMenu::item:selected { background-color: #88C0D0; color: black; }
        """)
        rm_action = menu.addAction("Remove from Playlist")
        rm_action.triggered.connect(lambda: self.remove_song(song_data))
        
        menu.exec(item_widget.mapToGlobal(pos))

    def remove_song(self, song_data):
        if self.current_playlist_id:
            self.db.remove_from_playlist(self.current_playlist_id, song_data['filepath'])
            global_event_bus.playlist_content_changed.emit(self.current_playlist_id)
            global_event_bus.playlists_updated.emit()

