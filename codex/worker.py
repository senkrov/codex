import os
import requests
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
from tmdb import TMDbAPI
from cache import CACHE_DIR, get_cache_path

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """
    download_finished = pyqtSignal(str, bytes)
    season_details_finished = pyqtSignal(dict)
    cache_cleanup_finished = pyqtSignal()

class ImageDownloader(QRunnable):
    """
    A QRunnable worker to download an image in the background.
    """
    def __init__(self, poster_path):
        super().__init__()
        self.poster_path = poster_path
        self.signals = WorkerSignals()

    def run(self):
        """Execute the download."""
        if not self.poster_path:
            return

        try:
            image_url = f"https://image.tmdb.org/t/p/w200{self.poster_path}"
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            image_data = response.content
            self.signals.download_finished.emit(self.poster_path, image_data)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image {self.poster_path}: {e}")

class SeasonDetailsDownloader(QRunnable):
    """
    A QRunnable worker to download season details in the background.
    """
    def __init__(self, show_id, season_number):
        super().__init__()
        self.show_id = show_id
        self.season_number = season_number
        self.signals = WorkerSignals()
        self.tmdb_api = TMDbAPI('df63e75244330de0737ce6f6d2f688ce')

    def run(self):
        """Execute the download."""
        if not self.show_id or self.season_number is None:
            return
        
        season_details = self.tmdb_api.get_show_season_details(self.show_id, self.season_number)
        if season_details:
            self.signals.season_details_finished.emit(season_details)

class CacheCleanupWorker(QRunnable):
    """
    A QRunnable worker to clean up the cache.
    """
    def __init__(self, movies, shows):
        super().__init__()
        self.movies = movies
        self.shows = shows
        self.signals = WorkerSignals()

    def run(self):
        """Execute the cleanup."""
        if not os.path.exists(CACHE_DIR):
            return

        valid_cache_files = set()
        for movie in self.movies:
            if movie.get('poster_path'):
                valid_cache_files.add(os.path.basename(get_cache_path(movie['poster_path'])))
        
        for show in self.shows:
            if show.get('poster_path'):
                valid_cache_files.add(os.path.basename(get_cache_path(show['poster_path'])))
            for season in show.get('seasons', []):
                if season.get('poster_path'):
                    valid_cache_files.add(os.path.basename(get_cache_path(season['poster_path'])))

        for filename in os.listdir(CACHE_DIR):
            if filename not in valid_cache_files:
                try:
                    os.remove(os.path.join(CACHE_DIR, filename))
                except OSError as e:
                    print(f"Error removing cached file: {e}")
        
        self.signals.cache_cleanup_finished.emit()
