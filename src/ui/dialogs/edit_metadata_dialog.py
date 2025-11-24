import os
import re
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QFrame

from src.database.db_manager import DBManager
from src.utils.events import global_event_bus
from src.core.metadata_editor import MetadataEditor

class EditMetadataDialog(QDialog):
    def __init__(self, song_data, parent=None):
        super().__init__(parent)
        self.song_data = song_data
        self.new_cover_path = None
        self.setWindowTitle("Edit Song Info")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog { background-color: #25262B; color: white; }
            QLineEdit { padding: 10px; border-radius: 4px; background: #3B4252; color: white; border: 1px solid #4C566A; }
            QLineEdit:focus { border: 1px solid #88C0D0; }
            QPushButton { padding: 8px 16px; border-radius: 4px; background: #4C566A; color: white; font-weight: bold; border: none;}
            QPushButton:hover { background: #5E81AC; }
            QLabel { color: #D8DEE9; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        img_layout = QVBoxLayout()
        self.lbl_cover = QLabel()
        self.lbl_cover.setFixedSize(160, 160)
        self.lbl_cover.setStyleSheet("background-color: #2E3440; border: 2px dashed #4C566A; border-radius: 8px;")
        self.lbl_cover.setScaledContents(True)
        self.lbl_cover.setAlignment(Qt.AlignCenter)
        self.lbl_cover.setCursor(Qt.PointingHandCursor)
        self.lbl_cover.mousePressEvent = self.browse_image
        
        if self.song_data.get('cover_path'):
            self.lbl_cover.setPixmap(QPixmap(self.song_data['cover_path']))
        else:
            self.lbl_cover.setText("Click to Change\nCover Art")

        img_layout.addWidget(self.lbl_cover, alignment=Qt.AlignCenter)
        img_hint = QLabel("(Click image to change)")
        img_hint.setStyleSheet("font-size: 10px; color: #666;")
        img_layout.addWidget(img_hint, alignment=Qt.AlignCenter)
        layout.addLayout(img_layout)

        self.input_title = QLineEdit(self.song_data.get('title', ''))
        self.input_title.setPlaceholderText("Song Title")
        
        self.input_artist = QLineEdit(self.song_data.get('artist', ''))
        self.input_artist.setPlaceholderText("Artist Name")
        
        self.input_album = QLineEdit(self.song_data.get('album', ''))
        self.input_album.setPlaceholderText("Album Name")
        
        layout.addWidget(self.input_title)
        layout.addWidget(self.input_artist)
        layout.addWidget(self.input_album)
        
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save Changes")
        btn_save.setStyleSheet("background-color: #88C0D0; color: #2E3440;")
        btn_save.clicked.connect(self.save_changes)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("background-color: transparent; border: 1px solid #4C566A; color: #D8DEE9;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def browse_image(self, event):
        path, _ = QFileDialog.getOpenFileName(self, "Select Cover Art", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.new_cover_path = path
            self.lbl_cover.setPixmap(QPixmap(path))

    def sanitize_filename(self, name):
        return re.sub(r'[<>:"/\\|?*]', '', name).strip()

    def save_changes(self):
        title = self.input_title.text().strip()
        artist = self.input_artist.text().strip()
        album = self.input_album.text().strip()
        
        if not title:
            QMessageBox.warning(self, "Error", "Title cannot be empty")
            return

        current_path = self.song_data['filepath']
        dir_name = os.path.dirname(current_path)
        ext = os.path.splitext(current_path)[1]
        
        editor = MetadataEditor(current_path)
        success = editor.save(title, artist, album, self.new_cover_path)
        
        if not success:
            QMessageBox.critical(self, "Error", "Failed to write tags. File might be in use.")
            return

        new_filename = f"{self.sanitize_filename(title)}{ext}"
        if artist:
            new_filename = f"{self.sanitize_filename(artist)} - {self.sanitize_filename(title)}{ext}"

        new_path = os.path.join(dir_name, new_filename)
        
        final_path = current_path
        
        if new_path != current_path:
            try:
                os.rename(current_path, new_path)
                final_path = new_path
            except OSError as e:
                QMessageBox.warning(self, "Rename Failed", f"Could not rename file. Is it playing?\nTags were saved, but filename remains.\nError: {e}")
                final_path = current_path

        db = DBManager()
        final_cover = self.new_cover_path if self.new_cover_path else self.song_data.get('cover_path')
        
        db.update_song_metadata(self.song_data['id'], title, artist, album, final_cover, final_path)
        
        global_event_bus.library_updated.emit()
        self.accept()

