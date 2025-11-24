from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QFontMetrics
from PySide6.QtWidgets import QLabel, QSizePolicy

class MarqueeLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._offset = 0
        self._text_width = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.scroll_step)
        self._scroll_speed = 30
        self._pause_counter = 0
        self._is_scrolling = False
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    def setText(self, text):
        super().setText(text)
        self.update_metrics()

    def resizeEvent(self, event):
        self.update_metrics()
        super().resizeEvent(event)

    def update_metrics(self):
        fm = QFontMetrics(self.font())
        self._text_width = fm.horizontalAdvance(self.text())
        
        if self._text_width > self.width():
            self._is_scrolling = True
            self._offset = 0
            if not self._timer.isActive():
                self._timer.start(self._scroll_speed)
        else:
            self._is_scrolling = False
            self._offset = 0
            self._timer.stop()
            self.update()

    def scroll_step(self):
        if not self._is_scrolling:
            return

        if self._offset == 0:
            if self._pause_counter < 40:
                self._pause_counter += 1
                return
            self._pause_counter = 0

        self._offset += 1
        if self._offset > (self._text_width + self.width()/3):
            self._offset = 0
            self._pause_counter = 0
            
        self.update()

    def paintEvent(self, event):
        if not self._is_scrolling:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        foreground_color = self.palette().color(self.foregroundRole())
        painter.setPen(foreground_color)
        
        y = (self.height() + QFontMetrics(self.font()).ascent()) // 2 - 2
        
        painter.drawText(-self._offset, y, self.text())
        painter.end()

