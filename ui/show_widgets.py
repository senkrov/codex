from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QThreadPool
from cache import get_image_from_cache, save_image_to_cache
from worker import ImageDownloader, WorkerSignals

from ui.widgets import MediaCard

class ShowCard(MediaCard):
    """
    A widget to display show information in a card format.
    """
    def __init__(self, show_data, pixmap_cache=None, parent=None):
        super().__init__(
            title=show_data['title'],
            poster_path=show_data.get('poster_path'),
            year=None,
            pixmap_cache=pixmap_cache,
            parent=parent
        )
        self.show_data = show_data

class SeasonCard(MediaCard):
    """
    A widget to display season information.
    """
    def __init__(self, show_id, season_data, pixmap_cache=None, parent=None):
        super().__init__(
            title=season_data['name'],
            poster_path=season_data.get('poster_path'),
            year=None,
            pixmap_cache=pixmap_cache,
            parent=parent
        )
        self.show_id = show_id
        self.season_data = season_data

class PodcastCard(MediaCard):
    """
    A widget to display podcast information in a card format.
    """
    def __init__(self, podcast_data, pixmap_cache=None, parent=None):
        super().__init__(
            title=podcast_data['title'],
            poster_path=podcast_data.get('poster_path'),
            year=None,
            pixmap_cache=pixmap_cache,
            parent=parent
        )
        self.podcast_data = podcast_data