import os
import mimetypes
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB

from src.utils.config import Config

class MetadataEditor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.audio = None
        try:
            self.audio = MP3(filepath, ID3=ID3)
        except Exception:
            try:
                self.audio = MP3(filepath)
                self.audio.add_tags()
            except Exception as e:
                print(f"Error opening file for editing: {e}")

    def save(self, title, artist, album, cover_path=None):
        if not self.audio:
            return False
        try:
            if title:
                self.audio.tags.add(TIT2(encoding=3, text=title))
            if artist:
                self.audio.tags.add(TPE1(encoding=3, text=artist))
            if album:
                self.audio.tags.add(TALB(encoding=3, text=album))
            if cover_path and os.path.exists(cover_path):
                mime_type, _ = mimetypes.guess_type(cover_path)
                mime_type = mime_type or 'image/jpeg'
                with open(cover_path, 'rb') as img:
                    self.audio.tags.add(
                        APIC(
                            encoding=3,
                            mime=mime_type,
                            type=3,
                            desc=u'Cover',
                            data=img.read()
                        )
                    )
            self.audio.save()
            return True
        except Exception as e:
            print(f"Error saving tags: {e}")
            return False

