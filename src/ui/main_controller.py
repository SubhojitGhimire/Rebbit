from PySide6.QtCore import QObject

from src.core.player import Player
from src.ui.collapsed_view import CollapsedView
from src.ui.expanded_view.expanded_view import ExpandedView

class MainController(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.player = Player()
        
        self.collapsed_view = CollapsedView()
        self.expanded_view = ExpandedView(app)
        
        self.connect_signals()
        self.show_collapsed()

    def connect_signals(self):
        self.collapsed_view.expand_requested.connect(self.show_expanded)
        self.collapsed_view.quit_requested.connect(self.app.quit)
        self.expanded_view.minimize_requested.connect(self.show_collapsed)
        self.expanded_view.quit_requested.connect(self.app.quit)

        self.expanded_view.library_tab.play_requested.connect(self.handle_play_request)
        self.expanded_view.playlists_tab.play_requested.connect(self.handle_play_request)

        self.collapsed_view.btn_play.clicked.connect(self.player.toggle_play)
        self.collapsed_view.btn_next.clicked.connect(self.player.next)
        self.collapsed_view.btn_prev.clicked.connect(self.player.prev)
        self.collapsed_view.slider.seek_request.connect(self.handle_seek)

        bar = self.expanded_view.player_bar
        
        bar.play_clicked.connect(self.player.toggle_play)
        bar.next_clicked.connect(self.player.next)
        bar.prev_clicked.connect(self.player.prev)
        bar.seek_requested.connect(self.handle_seek)
        bar.volume_changed.connect(self.player.audio_output.setVolume)
        bar.shuffle_toggled.connect(self.player.toggle_shuffle)
        bar.repeat_toggled.connect(self.player.toggle_repeat)

        self.player.state_changed.connect(self.sync_play_state)
        self.player.song_changed.connect(self.sync_song_info)
        
        self.player.position_changed.connect(self.sync_progress)
        self.player.duration_changed.connect(self.sync_duration)
        
        self.player.shuffle_changed.connect(bar.update_shuffle_state)
        self.player.repeat_changed.connect(bar.update_repeat_state)

    def handle_play_request(self, songs, index, shuffle):
        if shuffle:
            if not self.player.is_shuffle:
                self.player.toggle_shuffle() 
        self.player.load_queue(songs, index)

    def handle_seek(self, position):
        self.player.player.setPosition(position)
        if not self.collapsed_view.slider.is_dragging:
            self.collapsed_view.slider.setValue(position)
        if not self.expanded_view.player_bar.seek_slider.is_dragging:
            self.expanded_view.player_bar.seek_slider.setValue(position)

    def sync_play_state(self, is_playing):
        self.collapsed_view.set_playing_state(is_playing)
        self.expanded_view.player_bar.set_playing(is_playing)

    def sync_song_info(self, song_data):
        self.collapsed_view.update_song_info(song_data)
        self.expanded_view.player_bar.update_info(song_data)

    def sync_duration(self, duration):
        self.collapsed_view.update_duration(duration)
        self.expanded_view.player_bar.update_duration(duration)

    def sync_progress(self, position):
        self.collapsed_view.update_position(position)
        self.expanded_view.player_bar.update_progress(position)

    def show_collapsed(self):
        self.expanded_view.hide()
        self.collapsed_view.show()

    def show_expanded(self):
        self.collapsed_view.hide()
        self.expanded_view.show()
        self.expanded_view.activateWindow()

