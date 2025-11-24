import os
import hashlib
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

from src.utils.config import Config

class MetadataExtractor:
    @staticmethod
    def extract(filepath):
        data = {
            'filepath': filepath,
            'title': os.path.basename(filepath),
            'artist': 'Unknown Artist',
            'album': 'Unknown Album',
            'duration': 0,
            'cover_path': None
        }

        try:
            audio = MP3(filepath, ID3=ID3)
            data['duration'] = int(audio.info.length)
            if audio.tags:
                if 'TIT2' in audio.tags: data['title'] = str(audio.tags['TIT2'])
                if 'TPE1' in audio.tags: data['artist'] = str(audio.tags['TPE1'])
                if 'TALB' in audio.tags: data['album'] = str(audio.tags['TALB'])
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        hash_name = hashlib.md5(filepath.encode()).hexdigest()
                        ext = 'png' if 'png' in tag.mime else 'jpg'
                        image_filename = f"{hash_name}.{ext}"
                        save_path = Config.BASE_DIR / "assets" / "cache" / image_filename
                        if not save_path.exists():
                            with open(save_path, 'wb') as img:
                                img.write(tag.data)
                        data['cover_path'] = str(save_path)
                        break
        except Exception as e:
            print(f"Error reading metadata for {filepath}: {e}")
        return data

