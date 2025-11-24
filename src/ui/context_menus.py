from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu, QInputDialog, QMessageBox

from src.database.db_manager import DBManager
from src.utils.events import global_event_bus
from src.ui.dialogs.edit_metadata_dialog import EditMetadataDialog

class SongContextMenu:
    @staticmethod
    def show(parent, song_data, global_pos, item_widget=None):
        menu = QMenu(parent)
        menu.setStyleSheet("""
            QMenu { background-color: #25262B; border: 1px solid #3E4045; padding: 5px; }
            QMenu::item { padding: 5px 20px; color: white; }
            QMenu::item:selected { background-color: #88C0D0; color: black; }
        """)

        add_to_playlist = menu.addMenu("Add to Playlist")
        db = DBManager()
        playlists = db.get_playlists()
        new_pl_action = add_to_playlist.addAction("+ New Playlist")
        new_pl_action.triggered.connect(lambda: SongContextMenu.create_and_add(parent, song_data))
        add_to_playlist.addSeparator()
        for pl in playlists:
            action = add_to_playlist.addAction(f"{pl['name']} ({pl['song_count']})")
            action.triggered.connect(lambda checked=False, pid=pl['id']: SongContextMenu.add_to_existing(pid, song_data))
        
        menu.addSeparator()
        edit_action = menu.addAction("Edit Info")
        edit_action.triggered.connect(lambda: SongContextMenu.open_edit_dialog(parent, song_data))
        menu.exec(global_pos)

    @staticmethod
    def open_edit_dialog(parent, song_data):
        dialog = EditMetadataDialog(song_data, parent)
        dialog.exec()
    
    @staticmethod
    def create_and_add(parent, song_data):
        name, ok = QInputDialog.getText(parent, "New Playlist", "Playlist Name:")
        if ok and name:
            db = DBManager()
            if db.create_playlist(name):
                global_event_bus.playlists_updated.emit() 
                
                playlists = db.get_playlists()
                for p in playlists:
                    if p['name'] == name:
                        SongContextMenu.add_to_existing(p['id'], song_data)
                        break
            else:
                QMessageBox.warning(parent, "Error", "Playlist name already exists!")

    @staticmethod
    def add_to_existing(playlist_id, song_data):
        db = DBManager()
        db.add_to_playlist(playlist_id, song_data['filepath'])
        global_event_bus.playlists_updated.emit()
        global_event_bus.playlist_content_changed.emit(playlist_id)

