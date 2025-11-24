from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt, Signal

class CustomSlider(QSlider):
    seek_request = Signal(int) 
    
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.is_dragging = False
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #3B4252;
                height: 6px;
                background: #2E3440;
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #88C0D0;
                border: 1px solid #88C0D0;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #81A1C1;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #88C0D0;
                border-radius: 3px;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            val = self._pixel_to_value(event.pos().x())
            self.setValue(val)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            val = self._pixel_to_value(event.pos().x())
            self.setValue(val)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.seek_request.emit(self.value())
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def _pixel_to_value(self, x):
        width = self.width()
        if width <= 0: return 0
        x = max(0, min(x, width))
        span = self.maximum() - self.minimum()
        return int(self.minimum() + (span * (x / width)))

