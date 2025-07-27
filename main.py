import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QScrollArea, QGridLayout, 
                             QStyle, QStackedWidget, QLabel, QGraphicsView, QGraphicsScene)
from PyQt6.QtCore import Qt, QThreadPool, QPointF, QPropertyAnimation
from PyQt6.QtGui import QPixmap, QFont
from functools import partial
from scanner import scan_media
from ui.widgets import MediaCard
from ui.show_widgets import ShowCard, SeasonCard
from ui.episode_widgets import EpisodeWidget
from ui.category_widgets import ClickableCategoryCard
from ui.main_view import MainView
from ui.video_player import VideoPlayer
from ui.settings_view import SettingsView
from ui.animated_season_card import AnimatedSeasonCard
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

        self.loading_label = QLabel("Loading media...", self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.hide()
        self.main_layout.addWidget(self.loading_label)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)
        
        # Category View (New Main Screen)
        self.category_view = MainView()
        self.category_view.category_selected.connect(self.show_media_grid)
        self.stack.addWidget(self.category_view)

        # Settings View
        self.settings_view = SettingsView(self)
        self.stack.addWidget(self.settings_view)

        # Movies Grid View
        self.movies_grid_view = QWidget()
        self.movies_layout = QGridLayout(self.movies_grid_view)
        self.movies_scroll_area = QScrollArea()
        self.movies_scroll_area.setWidgetResizable(True)
        self.movies_scroll_area.setWidget(self.movies_grid_view)
        self.stack.addWidget(self.movies_scroll_area)

        # Shows Grid View
        self.shows_grid_view = QWidget()
        self.shows_layout = QGridLayout(self.shows_grid_view)
        self.shows_scroll_area = QScrollArea()
        self.shows_scroll_area.setWidgetResizable(True)
        self.shows_scroll_area.setWidget(self.shows_grid_view)
        self.stack.addWidget(self.shows_scroll_area)
        
        # Season View
        self.season_scene = QGraphicsScene()
        self.season_view = QGraphicsView(self.season_scene)
        self.season_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.season_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.stack.addWidget(self.season_view)

        # Episode View
        self.episode_scene = QGraphicsScene()
        self.episode_view = QGraphicsView(self.episode_scene)
        self.episode_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.episode_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.stack.addWidget(self.episode_view)

    def load_initial_media(self):
        media_path = load_media_path()
        if media_path and os.path.exists(media_path):
            self.scan_and_display_media(media_path)
        else:
            self.prompt_for_media_path()
            self.stack.setCurrentWidget(self.category_view)

    def prompt_for_media_path(self):
        media_path = QFileDialog.getExistingDirectory(self, 'Select Media Directory')
        if media_path:
            save_media_path(media_path)
            self.scan_and_display_media(media_path)

    def scan_and_display_media(self, media_path):
        self.loading_label.show()
        movies, self.shows = scan_media(media_path)
        metadata_worker = MetadataWorker(movies, self.shows, self.worker_signals)
        self.threadpool.start(metadata_worker)

    def populate_ui(self, movies, shows):
        self.loading_label.hide()
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

        self.current_row = 0
        self.current_col = 0
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
            for season in show.get('seasons', []):
                if season.get('poster_path'):
                    worker = ImageDownloader(season['poster_path'], self.worker_signals)
                    self.threadpool.start(worker)
                if season.get('episodes_details'):
                    for episode_data in season['episodes_details']:
                        if episode_data.get('still_path'):
                            worker = ImageDownloader(episode_data['still_path'], self.worker_signals)
                            self.threadpool.start(worker)

    def on_image_downloaded(self, poster_path, image_data):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.pixmap_cache[poster_path] = pixmap

    def show_media_grid(self, category_type):
        self.current_row = 0
        self.current_col = 0
        if category_type == "movies":
            self.stack.setCurrentWidget(self.movies_scroll_area)
        elif category_type == "shows":
            self.stack.setCurrentWidget(self.shows_scroll_area)
        self.update_selection()

    def show_season_view(self, show_index):
        self.current_show_index = show_index
        self.season_scene.clear()
        self.season_cards = []
        
        show = self.shows[show_index]
        
        sorted_seasons = sorted(show['seasons'], key=natural_sort_key)
        
        for i, season in enumerate(sorted_seasons):
            card = AnimatedSeasonCard(show.get('id'), season_data=season, pixmap_cache=self.pixmap_cache)
            card.season_card.clicked.connect(partial(self.show_episode_view, i))
            self.season_scene.addItem(card)
            self.season_cards.append(card)
        
        self.stack.setCurrentWidget(self.season_view)
        self.current_row = 0
        self.current_col = 0
        self.update_selection()

    def show_episode_view(self, season_index):
        self.episode_scene.clear()
        self.episode_widgets = []

        show = self.shows[self.current_show_index]
        sorted_seasons = sorted(show['seasons'], key=natural_sort_key)
        season = sorted_seasons[season_index]
        
        for episode_data in season.get('episodes', []):
            widget = EpisodeWidget(episode_data, pixmap_cache=self.pixmap_cache)
            self.episode_scene.addWidget(widget)
            self.episode_widgets.append(widget)

        self.stack.setCurrentWidget(self.episode_view)
        self.current_row = 0
        self.current_col = 0
        self.update_selection()

    def show_settings_view(self):
        self.stack.setCurrentWidget(self.settings_view)

    def show_main_view(self):
        self.stack.setCurrentWidget(self.category_view)
        self.update_selection()

    def keyPressEvent(self, event):
        key = event.key()
        current_widget = self.stack.currentWidget()

        if key == Qt.Key.Key_O:
            self.show_settings_view()
            return
        elif key == Qt.Key.Key_H:
            if current_widget == self.movies_scroll_area or current_widget == self.shows_scroll_area:
                self.show_main_view()
            elif current_widget == self.season_view:
                self.show_media_grid("shows")
            elif current_widget == self.episode_view:
                self.show_season_view(self.current_show_index)
            return

        if current_widget == self.season_view or current_widget == self.episode_view:
            if key == Qt.Key.Key_J:
                self.current_col = max(self.current_col - 1, 0)
            elif key == Qt.Key.Key_K:
                self.current_col = min(self.current_col + 1, len(self.season_cards) - 1)
            self.update_selection()
            return
        
        if key == Qt.Key.Key_J:
            self.current_col = max(self.current_col - 1, 0)
        elif key == Qt.Key.Key_K:
            self.current_col = min(self.current_col + 1, 3)
        elif key == Qt.Key.Key_U:
            self.current_row = max(self.current_row - 1, 0)
        elif key == Qt.Key.Key_D:
            self.current_row = min(self.current_row + 1, 4)
        elif key in (Qt.Key.Key_L, Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            if current_widget == self.movies_scroll_area:
                index = self.current_row * 4 + self.current_col
                if 0 <= index < len(self.movie_cards):
                    self.play_media(self.movies[index]['path'])
            elif current_widget == self.shows_scroll_area:
                index = self.current_row * 4 + self.current_col
                if 0 <= index < len(self.show_cards):
                    self.show_season_view(index)
            elif current_widget == self.category_view:
                if self.current_col == 0:
                    self.show_media_grid("movies")
                else:
                    self.show_media_grid("shows")
        
        self.update_selection()

    def play_media(self, path):
        self.video_player = VideoPlayer(path)
        self.video_player.show()

    def update_selection(self):
        current_widget = self.stack.currentWidget()

        if current_widget == self.season_view:
            center_x = self.season_view.width() / 2
            for i, card in enumerate(self.season_cards):
                card.set_selected(i == self.current_col)
                distance = i - self.current_col
                
                card_width = card.boundingRect().width()
                pos_x = center_x - card_width / 2

                if distance == 0:
                    scale = 1.5
                    opacity = 1.0
                    rotation = 0
                elif distance in [-1, 1]:
                    scale = 1.0
                    opacity = 0.5
                    rotation = 30 if distance == -1 else -30
                    pos_x += -250 if distance == -1 else 250
                elif distance in [-2, 2]:
                    scale = 0.8
                    opacity = 0.2
                    rotation = 45 if distance == -2 else -45
                    pos_x += -450 if distance == -2 else 450
                else:
                    scale = 0.8
                    opacity = 0.0
                    rotation = 45 if distance < 0 else -45
                    pos_x += -600 if distance < 0 else 600
                
                card.animate_to(QPointF(pos_x, 0), scale, opacity, rotation)
            return

        for card_list in [self.movie_cards, self.show_cards, self.category_view.cards]:
            for card in card_list:
                card.setStyleSheet("")

        if current_widget == self.movies_scroll_area:
            cards = self.movie_cards
            layout = self.movies_layout
        elif current_widget == self.shows_scroll_area:
            cards = self.show_cards
            layout = self.shows_layout
        elif current_widget == self.category_view:
            cards = self.category_view.cards
            layout = self.category_view.layout()
        else:
            return

        if not cards: return

        index = self.current_row * 4 + self.current_col
        if 0 <= index < len(cards):
            card = cards[index]
            card.setStyleSheet("border: 2px solid #0078D7;")

def main():
    app = QApplication(sys.argv)
    font = QFont("Roboto")
    app.setFont(font)
    codex = Codex()
    codex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()