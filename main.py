import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QScrollArea, QGridLayout, QTabWidget, 
                             QStyle, QStackedWidget, QLabel)
from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtGui import QPixmap
from functools import partial
from scanner import scan_media
from ui.widgets import MediaCard
from ui.show_widgets import ShowCard, SeasonCard
from ui.episode_widgets import EpisodeWidget
from tmdb import TMDbAPI
from config import save_media_path, load_media_path
from worker import CacheCleanupWorker, WorkerSignals, ImageDownloader, MetadataWorker

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s['name'])]

class Codex(QWidget):
    def __init__(self):
        super().__init__()
        self.tmdb_api = TMDbAPI('df63e75244330de0737ce6f6d2f688ce')
        self.movie_cards = []
        self.show_cards = []
        self.season_cards = []
        self.episode_widgets = []
        self.current_show_index = -1
        self.current_row = 0
        self.current_col = 0
        self.threadpool = QThreadPool()
        self.pixmap_cache = {}
        self.worker_signals = WorkerSignals()
        self.worker_signals.download_finished.connect(self.on_image_downloaded)
        self.worker_signals.metadata_finished.connect(self.populate_ui)
        self.initUI()
        self.load_initial_media()

    def initUI(self):
        self.setWindowTitle('Codex')
        self.setFixedSize(1024, 768)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # Main view with tabs
        self.main_view = QWidget()
        self.main_view_layout = QVBoxLayout(self.main_view)
        self.tabs = QTabWidget()
        self.main_view_layout.addWidget(self.tabs)
        self.stack.addWidget(self.main_view)

        # Movies Tab
        self.movies_tab = QWidget()
        self.movies_layout = QGridLayout(self.movies_tab)
        self.movies_scroll_area = QScrollArea()
        self.movies_scroll_area.setWidgetResizable(True)
        self.movies_scroll_area.setWidget(self.movies_tab)
        self.tabs.addTab(self.movies_scroll_area, "Movies")

        # Shows Tab
        self.shows_tab = QWidget()
        self.shows_layout = QGridLayout(self.shows_tab)
        self.shows_scroll_area = QScrollArea()
        self.shows_scroll_area.setWidgetResizable(True)
        self.shows_scroll_area.setWidget(self.shows_tab)
        self.tabs.addTab(self.shows_scroll_area, "Shows")
        
        # Season View
        self.season_view = QWidget()
        self.season_view_layout = QVBoxLayout(self.season_view)
        self.season_grid = QGridLayout()
        self.season_view_layout.addLayout(self.season_grid)
        back_button_seasons = QPushButton("Back to Shows")
        back_button_seasons.clicked.connect(self.show_main_view)
        self.season_view_layout.addWidget(back_button_seasons)
        self.stack.addWidget(self.season_view)

        # Episode View
        self.episode_view = QWidget()
        self.episode_view_layout = QVBoxLayout(self.episode_view)
        
        self.episode_scroll_area = QScrollArea()
        self.episode_scroll_area.setWidgetResizable(True)
        
        self.episode_list_container = QWidget()
        self.episode_list = QVBoxLayout(self.episode_list_container)
        self.episode_list.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft) # Align items to top-left
        
        self.episode_scroll_area.setWidget(self.episode_list_container)
        self.episode_view_layout.addWidget(self.episode_scroll_area)

        back_button_episodes = QPushButton("Back to Seasons")
        back_button_episodes.clicked.connect(self.show_season_view_from_episode)
        self.episode_view_layout.addWidget(back_button_episodes)
        self.stack.addWidget(self.episode_view)

        self.change_dir_button = QPushButton()
        self.change_dir_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        self.change_dir_button.clicked.connect(self.prompt_for_media_path)
        self.tabs.setCornerWidget(self.change_dir_button)

    def load_initial_media(self):
        media_path = load_media_path()
        if media_path and os.path.exists(media_path):
            self.scan_and_display_media(media_path)
        else:
            self.prompt_for_media_path()

    def prompt_for_media_path(self):
        media_path = QFileDialog.getExistingDirectory(self, 'Select Media Directory')
        if media_path:
            save_media_path(media_path)
            self.scan_and_display_media(media_path)

    def scan_and_display_media(self, media_path):
        movies, self.shows = scan_media(media_path)
        metadata_worker = MetadataWorker(movies, self.shows, self.worker_signals)
        self.threadpool.start(metadata_worker)

    def populate_ui(self, movies, shows):
        self.movies = movies
        self.shows = shows

        for card in self.movie_cards + self.show_cards:
            card.setParent(None)
        self.movie_cards, self.show_cards = [], []
        
        cleanup_worker = CacheCleanupWorker(self.movies, self.shows, self.worker_signals)
        self.threadpool.start(cleanup_worker)

        self.preload_images(self.movies, self.shows)

        row, col = 0, 0
        for movie in self.movies:
            card = MediaCard(movie['title'], movie['year'], movie.get('poster_path'), self.pixmap_cache)
            self.movies_layout.addWidget(card, row, col)
            self.movie_cards.append(card)
            col += 1
            if col > 3: col = 0; row += 1
        
        row, col = 0, 0
        for i, show in enumerate(self.shows):
            card = ShowCard(show, self.pixmap_cache)
            card.clicked.connect(partial(self.show_season_view, i))
            self.shows_layout.addWidget(card, row, col)
            self.show_cards.append(card)
            col += 1
            if col > 3: col = 0; row += 1

        self.update_selection()

    def preload_images(self, movies, shows):
        for movie in movies:
            if movie.get('poster_path'):
                worker = ImageDownloader(movie['poster_path'], self.worker_signals)
                self.threadpool.start(worker)
        for show in shows:
            if show.get('poster_path'):
                worker = ImageDownloader(show['poster_path'], self.worker_signals)
                self.threadpool.start(worker)

    def on_image_downloaded(self, poster_path, image_data):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.pixmap_cache[poster_path] = pixmap

    def show_season_view(self, show_index):
        self.current_show_index = show_index
        for card in self.season_cards:
            card.setParent(None)
        self.season_cards = []
        
        show = self.shows[show_index]
        
        sorted_seasons = sorted(show['seasons'], key=natural_sort_key)
        
        row, col = 0, 0
        for i, season in enumerate(sorted_seasons):
            card = SeasonCard(show.get('id'), season_data=season, pixmap_cache=self.pixmap_cache)
            card.clicked.connect(partial(self.show_episode_view, i))
            self.season_grid.addWidget(card, row, col)
            self.season_cards.append(card)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        self.stack.setCurrentWidget(self.season_view)

    def show_season_view_from_episode(self):
        self.show_season_view(self.current_show_index)

    def show_episode_view(self, season_index):
        for widget in self.episode_widgets:
            widget.setParent(None)
        self.episode_widgets = []

        show = self.shows[self.current_show_index]
        sorted_seasons = sorted(show['seasons'], key=natural_sort_key)
        season = sorted_seasons[season_index]
        
        for episode_data in season.get('episodes_details', []):
            widget = EpisodeWidget(episode_data, pixmap_cache=self.pixmap_cache)
            self.episode_list.addWidget(widget)
            self.episode_widgets.append(widget)

        self.stack.setCurrentWidget(self.episode_view)

    def show_main_view(self):
        self.stack.setCurrentWidget(self.main_view)

    def keyPressEvent(self, event):
        key = event.key()
        
        if self.stack.currentWidget() == self.main_view:
            current_cards = self.movie_cards if self.tabs.currentIndex() == 0 else self.show_cards
            layout = self.movies_layout if self.tabs.currentIndex() == 0 else self.shows_layout
        elif self.stack.currentWidget() == self.season_view:
            current_cards = self.season_cards
            layout = self.season_grid
        else:
            return

        if not current_cards: return

        rows = layout.rowCount()
        cols = layout.columnCount()

        if key == Qt.Key.Key_Right: self.current_col = min(self.current_col + 1, cols - 1)
        elif key == Qt.Key.Key_Left: self.current_col = max(self.current_col - 1, 0)
        elif key == Qt.Key.Key_Down: self.current_row = min(self.current_row + 1, rows - 1)
        elif key == Qt.Key.Key_Up: self.current_row = max(self.current_row - 1, 0)
        
        self.update_selection()

    def update_selection(self):
        if self.stack.currentWidget() == self.main_view:
            current_cards = self.movie_cards if self.tabs.currentIndex() == 0 else self.show_cards
            layout = self.movies_layout if self.tabs.currentIndex() == 0 else self.shows_layout
        elif self.stack.currentWidget() == self.season_view:
            current_cards = self.season_cards
            layout = self.season_grid
        else:
            return

        for i, card in enumerate(current_cards):
            row, col, _, _ = layout.getItemPosition(i)
            if row == self.current_row and col == self.current_col:
                card.setStyleSheet("border: 2px solid red;")
            else:
                card.setStyleSheet("")

def main():
    app = QApplication(sys.argv)
    codex = Codex()
    codex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
