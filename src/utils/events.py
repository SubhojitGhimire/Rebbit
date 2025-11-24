from PySide6.QtCore import QObject, Signal

class EventBus(QObject):
    library_updated = Signal() # When new songs are downloaded
    playlists_updated = Signal() # When a playlist is created/renamed/deleted
    playlist_content_changed = Signal(int) # When songs are added/removed from a specific playlist ID
global_event_bus = EventBus() # Global instance to be imported elsewhere

