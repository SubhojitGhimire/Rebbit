import random
from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

class RepeatMode:
    NONE = 0
    ALL = 1
    ONE = 2

class Player(QObject):
    state_changed = Signal(bool)
    song_changed = Signal(dict)
    position_changed = Signal(int)
    duration_changed = Signal(int)
    shuffle_changed = Signal(bool)
    repeat_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.original_queue = []
        self.queue = []
        self.current_index = -1
        self.is_shuffle = False
        self.repeat_mode = RepeatMode.NONE
        
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)

        self.player.mediaStatusChanged.connect(self.handle_media_status)
        self.player.positionChanged.connect(self.position_changed.emit)
        self.player.durationChanged.connect(self.duration_changed.emit)

    def load_queue(self, songs, start_index=0):
        self.original_queue = list(songs)
        if self.is_shuffle:
            first_song = songs[start_index]
            remaining = [s for i, s in enumerate(songs) if i != start_index]
            random.shuffle(remaining)
            self.queue = [first_song] + remaining
            self.current_index = 0
        else:
            self.queue = list(songs)
            self.current_index = start_index
            
        self.play_current()

    def play_current(self):
        if 0 <= self.current_index < len(self.queue):
            song = self.queue[self.current_index]
            self.player.setSource(QUrl.fromLocalFile(song['filepath']))
            self.player.play()
            self.state_changed.emit(True)
            self.song_changed.emit(song)

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.state_changed.emit(False)
        elif self.queue:
            self.player.play()
            self.state_changed.emit(True)

    def next(self):
        if not self.queue: return
        if self.repeat_mode == RepeatMode.ONE:
            self.player.setPosition(0)
            self.player.play()
        elif self.current_index < len(self.queue) - 1:
            self.current_index += 1
            self.play_current()
        elif self.repeat_mode == RepeatMode.ALL:
            self.current_index = 0
            self.play_current()
        else:
            self.player.stop()
            self.state_changed.emit(False)

    def prev(self):
        if self.player.position() > 3000:
            self.player.setPosition(0)
        elif self.current_index > 0:
            self.current_index -= 1
            self.play_current()
        elif self.repeat_mode == RepeatMode.ALL:
            self.current_index = len(self.queue) - 1
            self.play_current()

    def toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle
        if self.queue:
            current_song = self.queue[self.current_index]
            if self.is_shuffle:
                remaining = [s for s in self.original_queue if s != current_song]
                random.shuffle(remaining)
                self.queue = [current_song] + remaining
                self.current_index = 0
            else:
                self.queue = list(self.original_queue)
                for i, s in enumerate(self.queue):
                    if s['filepath'] == current_song['filepath']:
                        self.current_index = i
                        break
        self.shuffle_changed.emit(self.is_shuffle)

    def toggle_repeat(self):
        if self.repeat_mode == RepeatMode.NONE:
            self.repeat_mode = RepeatMode.ALL
        elif self.repeat_mode == RepeatMode.ALL:
            self.repeat_mode = RepeatMode.ONE
        else:
            self.repeat_mode = RepeatMode.NONE
            
        self.repeat_changed.emit(self.repeat_mode)

    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.next()

