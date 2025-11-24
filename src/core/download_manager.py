from PySide6.QtCore import QObject, Signal

from src.utils.config import Config
from src.core.downloader import DownloadWorker

class DownloadManager(QObject):
    task_added = Signal(object)
    task_finished = Signal(str)
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.active_tasks = []

    def start_download(self, url, title):
        save_dir = Config.DEFAULT_MUSIC_DIR
        worker = DownloadWorker(url, str(save_dir))
        worker.video_title = title 
        worker.finished.connect(lambda f: self.on_finished(worker, f))
        worker.error.connect(lambda e: self.on_error(worker, e))
        self.active_tasks.append(worker)
        self.task_added.emit(worker)
        worker.start()

    def on_finished(self, worker, filename):
        if worker in self.active_tasks:
            self.active_tasks.remove(worker)
        self.task_finished.emit(filename)

    def on_error(self, worker, err):
        print(f"Download Error: {err}")
        if worker in self.active_tasks:
            self.active_tasks.remove(worker)

