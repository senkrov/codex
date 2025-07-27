import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QScrollArea, QGridLayout, 
                             QStyle, QStackedWidget, QLabel, QGraphicsView, QGraphicsScene)
from PyQt6.QtCore import Qt, pyqtSignal, QThreadPool, QTimer, QPointF
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
from ui.animated_episode_card import AnimatedEpisodeCard
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
        self.update_season_card_positions()

    def show_episode_view(self, season_index):
        self.episode_scene.clear()
        self.episode_cards = []

        show = self.shows[self.current_show_index]
        sorted_seasons = sorted(show['seasons'], key=natural_sort_key)
        season = sorted_seasons[season_index]
        
        for episode_data in season.get('episodes_details', []):
            card = AnimatedEpisodeCard(episode_data, pixmap_cache=self.pixmap_cache)
            self.episode_scene.addItem(card)
            self.episode_cards.append(card)

        self.stack.setCurrentWidget(self.episode_view)
        self.current_row = 0
        self.current_col = 0 # Ensure first card is selected
        self.episode_view.horizontalScrollBar().setValue(0) # Reset scrollbar to left
        QTimer.singleShot(100, self.update_episode_card_positions) # Delay positioning with 100ms

    def update_episode_card_positions(self):
        if not self.episode_cards:
            return

        view_width = self.episode_view.viewport().width()
        card_width = self.episode_cards[0].boundingRect().width()
        num_cards = len(self.episode_cards)

        # 1. Narrow the focal point's travel range to reduce lateral movement
        start_x = view_width * 0.35
        end_x = view_width * 0.65
        
        if num_cards > 1:
            focal_point_x = start_x + (self.current_col / (num_cards - 1)) * (end_x - start_x)
        else:
            focal_point_x = view_width / 2

        for i, card in enumerate(self.episode_cards):
            distance = i - self.current_col

            # 2. Reduce spacing to bring cards closer
            card_spacing = 5  # Further reduced spacing
            offset = distance * (card_width * 0.2 + card_spacing) # Further reduced offset multiplier
            pos_x = focal_point_x + offset - (card_width / 2)

            if distance == 0:
                scale = 1.2
                opacity = 1.0
                rotation = 0
                card.set_selected(True)
                card.setZValue(num_cards)
            else:
                # 3. Make unfocused cards significantly smaller
                scale = 0.6
                opacity = 1.0
                card.set_selected(False)
                card.setZValue(num_cards - abs(distance))
                if distance < 0:
                    rotation = 25
                else:
                    rotation = -25

            card.set_properties_instantly(QPointF(pos_x, 0), scale, opacity, rotation)

    def update_season_card_positions(self):
        if not self.season_cards:
            return

        view_width = self.season_view.viewport().width()
        card_width = self.season_cards[0].boundingRect().width()
        num_cards = len(self.season_cards)

        # --- Dynamic Focal Point Calculation ---
        # The focal point moves from left to right as the selection changes.
        start_x = view_width * 0.15  # Focal point for the first card
        end_x = view_width * 0.85    # Focal point for the last card
        
        if num_cards > 1:
            focal_point_x = start_x + (self.current_col / (num_cards - 1)) * (end_x - start_x)
        else:
            focal_point_x = view_width / 2 # Center if only one card

        # --- Card Positioning and Visual Effects ---
        for i, card in enumerate(self.season_cards):
            distance = i - self.current_col

            # --- Position Calculation (Sprawling Layout) ---
            # The focused card is at focal_point_x.
            # Other cards are positioned relative to it, creating a fanned-out effect.
            card_spacing = 30
            offset = distance * (card_width * 0.4 + card_spacing)
            pos_x = focal_point_x + offset - (card_width / 2)

            # --- Visual Effect Calculation ---
            if distance == 0:
                # Focused card
                scale = 1.0
                opacity = 1.0
                rotation = 0
                card.set_selected(True)
                card.setZValue(num_cards)
            else:
                # Unfocused cards
                scale = 0.8  # Fixed scale for all unfocused cards
                opacity = 0.7 # Fixed opacity for all unfocused cards
                card.set_selected(False)
                card.setZValue(num_cards - abs(distance))
                
                # Determine rotation based on position relative to the focused card
                if distance < 0:
                    rotation = 25  # Positive rotation for cards to the left
                else:
                    rotation = -25 # Negative rotation for cards to the right

            card.set_properties_instantly(QPointF(pos_x, 0), scale, opacity, rotation)

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

        if current_widget == self.season_view:
            if key == Qt.Key.Key_J:
                self.current_col = max(self.current_col - 1, 0)
            elif key == Qt.Key.Key_K:
                self.current_col = min(self.current_col + 1, len(self.season_cards) - 1)
            elif key in (Qt.Key.Key_L, Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
                self.show_episode_view(self.current_col)
            self.update_season_card_positions()
            return
        elif current_widget == self.episode_view:
            if key == Qt.Key.Key_J:
                self.current_col = max(self.current_col - 1, 0)
            elif key == Qt.Key.Key_K:
                self.current_col = min(self.current_col + 1, len(self.episode_cards) - 1)
            self.update_episode_card_positions()
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
            # This logic is now handled by update_season_card_positions
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