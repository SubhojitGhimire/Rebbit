from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QFrame

class DownloadItem(QFrame):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.setFixedHeight(70)
        self.setStyleSheet("""
            DownloadItem {
                background-color: #2E3440;
                border-radius: 6px;
                border: 1px solid #3B4252;
            }
            QLabel { color: white; }
            QProgressBar {
                border: 1px solid #4C566A;
                border-radius: 4px;
                text-align: center;
                background-color: #2E3440;
            }
            QProgressBar::chunk { background-color: #88C0D0; }
        """)
        
        self.init_ui()
        self.connect_worker()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignVCenter)
        
        top_layout = QHBoxLayout()
        self.lbl_title = QLabel(getattr(self.worker, 'video_title', 'Unknown Download'))
        self.lbl_title.setStyleSheet("font-weight: bold;")
        
        self.lbl_status = QLabel("Starting...")
        self.lbl_status.setStyleSheet("color: #EBCB8B; font-size: 11px;")
        
        top_layout.addWidget(self.lbl_title)
        top_layout.addStretch()
        top_layout.addWidget(self.lbl_status)
        layout.addLayout(top_layout)
        
        self.pbar = QProgressBar()
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)
        self.pbar.setFixedHeight(10)
        self.pbar.setTextVisible(False)
        layout.addWidget(self.pbar)

    def connect_worker(self):
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)

    def update_progress(self, progress_str):
        self.lbl_status.setText(f"Downloading... {progress_str}")
        
        try:
            clean_str = progress_str.split(']')[-1].strip().replace('%','')
            val = float(clean_str)
            self.pbar.setValue(int(val))
        except:
            pass

    def on_finished(self, filename):
        self.lbl_status.setText("Completed")
        self.lbl_status.setStyleSheet("color: #A3BE8C;")
        self.pbar.setValue(100)

    def on_error(self, err):
        self.lbl_status.setText("Error")
        self.lbl_status.setStyleSheet("color: #BF616A;")

