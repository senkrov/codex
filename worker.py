import os
import re
import requests
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
from tmdb import TMDbAPI
from cache import CACHE_DIR, get_cache_path

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """
    download_finished = pyqtSignal(str, bytes)
    metadata_finished = pyqtSignal(list, list)
    single_show_metadata_finished = pyqtSignal(dict)
    cache_cleanup_finished = pyqtSignal()

class ImageDownloader(QRunnable):
    """
    A QRunnable worker to download an image in the background.
    """
    def __init__(self, poster_path, signals):
        super().__init__()
        self.poster_path = poster_path
        self.signals = signals

    def run(self):
        """Execute the download."""
        if not self.poster_path:
            return

        try:
            image_url = f"https://image.tmdb.org/t/p/w500{self.poster_path}"
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            image_data = response.content
            self.signals.download_finished.emit(self.poster_path, image_data)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image {self.poster_path}: {e}")

class MetadataWorker(QRunnable):
    """
    A QRunnable worker to fetch all metadata in the background.
    """
    def __init__(self, movies, shows, signals):
        super().__init__()
        self.movies = movies
        self.shows = shows
        self.signals = signals
        self.tmdb_api = TMDbAPI('df63e75244330de0737ce6f6d2f688ce')

    def run(self):
        """Execute the metadata fetching."""
        import time
        start_time = time.time()
        for movie in self.movies:
            search_results = self.tmdb_api.search_movie(movie['title'], movie['year'])
            if search_results and 'results' in search_results and search_results['results']:
                movie['poster_path'] = search_results['results'][0].get('poster_path')

        for show in self.shows:
            search_results = self.tmdb_api.search_show(show['title'])
            if search_results and 'results' in search_results and search_results['results']:
                show['poster_path'] = search_results['results'][0].get('poster_path')
                show['id'] = search_results['results'][0].get('id')
                # Season and episode details will be fetched on demand

        end_time = time.time()
        print(f"Metadata fetching completed in {end_time - start_time:.2f} seconds.")
        self.signals.metadata_finished.emit(self.movies, self.shows)

class CacheCleanupWorker(QRunnable):
    """
    A QRunnable worker to clean up the cache.
    """
    def __init__(self, movies, shows, signals):
        super().__init__()
        self.movies = movies
        self.shows = shows
        self.signals = signals

    def run(self):
        """Execute the cleanup."""
        print("Starting cache cleanup...")
        import time
        start_time = time.time()
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
        end_time = time.time()
        print(f"Cache cleanup completed in {end_time - start_time:.2f} seconds.")
        self.signals.cache_cleanup_finished.emit()

class SingleShowMetadataWorker(QRunnable):
    """
    A QRunnable worker to fetch metadata for a single show's seasons and episodes.
    """
    def __init__(self, show_data, signals):
        super().__init__()
        self.show_data = show_data
        self.signals = signals
        self.tmdb_api = TMDbAPI('df63e75244330de0737ce6f6d2f688ce')

    def run(self):
        print(f"Fetching season/episode metadata for {self.show_data.get('title')}...")
        import time
        start_time = time.time()

        show_id = self.show_data.get('id')
        if not show_id:
            print(f"Error: No TMDb ID for show {self.show_data.get('title')}")
            self.signals.single_show_metadata_finished.emit(self.show_data) # Emit even on error
            return

        for season in self.show_data['seasons']:
            season_number_match = re.search(r'\d+', season['name'])
            if season_number_match:
                season_number = int(season_number_match.group())
                season_details = self.tmdb_api.get_show_season_details(show_id, season_number)
                if season_details:
                    season['poster_path'] = season_details.get('poster_path')
                    processed_episodes = []
                    for episode in season_details.get('episodes', []):
                        processed_episodes.append({
                            'episode_number': episode.get('episode_number'),
                            'name': episode.get('name'),
                            'still_path': episode.get('still_path')
                        })
                    season['episodes_details'] = processed_episodes
        
        end_time = time.time()
        print(f"Finished fetching season/episode metadata for {self.show_data.get('title')} in {end_time - start_time:.2f} seconds.")
        self.signals.single_show_metadata_finished.emit(self.show_data)