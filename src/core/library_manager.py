import os
from PySide6.QtCore import QObject, Signal, QThread

from src.utils.config import Config
from src.database.db_manager import DBManager
from src.core.metadata import MetadataExtractor

class LibraryScanner(QThread):
    scan_finished = Signal()
    
    def run(self):
        db = DBManager()
        music_dir = Config.DEFAULT_MUSIC_DIR
        for root, dirs, files in os.walk(music_dir):
            for file in files:
                if file.lower().endswith('.mp3'):
                    full_path = os.path.join(root, file)
                    if not db.song_exists(full_path):
                        meta = MetadataExtractor.extract(full_path)
                        db.add_song(meta)
        self.scan_finished.emit()

class LibraryManager(QObject):
    library_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.scanner = LibraryScanner()
        self.scanner.scan_finished.connect(self.load_library)

    def refresh_library(self):
        if not self.scanner.isRunning():
            self.scanner.start()

    def load_library(self):
        songs = self.db.get_all_songs()
        self.library_changed.emit(songs)

