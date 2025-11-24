import yt_dlp
from PySide6.QtCore import QThread, Signal

class SearchWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'noplaylist': False,
            'limit': 5,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.query.strip().startswith(("http://", "https://", "www.")):
                    info = ydl.extract_info(self.query, download=False)
                    
                    results = []
                    if 'entries' in info:
                        playlist_data = {
                            'title': info.get('title', 'Unknown Playlist'),
                            'uploader': info.get('uploader', 'Unknown Uploader'),
                            'webpage_url': info.get('webpage_url', self.query),
                            'thumbnails': info.get('thumbnails', []),
                            'is_playlist': True,
                            'video_count': len(list(info['entries']))
                        }
                        results.append(playlist_data)
                    else:
                        info['is_playlist'] = False
                        results.append(info)
                else:
                    info = ydl.extract_info(f"ytsearch5:{self.query}", download=False)
                    if 'entries' in info:
                        results = info['entries']
                    else:
                        results = []
                self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class DownloadWorker(QThread):
    progress = Signal(str) 
    finished = Signal(str) 
    error = Signal(str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        def progress_hook(d):
            if d['status'] == 'downloading':
                if 'playlist_count' in d and d['playlist_count'] is not None:
                    index = d.get('playlist_index', 1)
                    total = d.get('playlist_count', '?')
                    pct = d.get('_percent_str', '0%').strip()
                    self.progress.emit(f"[{index}/{total}] {pct}")
                else:
                    p = d.get('_percent_str', '0%').strip()
                    self.progress.emit(p)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.save_path}/%(title)s.%(ext)s',
            'writethumbnail': True,
            'postprocessors': [
                {'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'},
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata'},
            ],
            'progress_hooks': [progress_hook],
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(self.url, download=True)
                self.finished.emit("Download Complete")
        except Exception as e:
            self.error.emit(str(e))

