from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QThreadPool
from cache import get_image_from_cache, save_image_to_cache
from worker import ImageDownloader, SeasonDetailsDownloader
import re

class ClickableQWidget(QWidget):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class ShowCard(ClickableQWidget):
    """
    A widget to display show information in a card format.
    """
    def __init__(self, show_data, parent=None):
        super().__init__(parent)
        self.show_data = show_data
        self.pixmap = None
        self.threadpool = QThreadPool()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.poster_label = QLabel()
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_poster()
        layout.addWidget(self.poster_label)

        self.title_label = QLabel(self.show_data['title'])
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

    def set_poster(self):
        poster_path = self.show_data.get('poster_path')
        print(f"ShowCard '{self.show_data['title']}': Setting poster with path: {poster_path}")
        if poster_path:
            cached_pixmap = get_image_from_cache(poster_path)
            if cached_pixmap:
                print(f"ShowCard '{self.show_data['title']}': Found poster in cache.")
                self.poster_label.setPixmap(cached_pixmap)
            else:
                print(f"ShowCard '{self.show_data['title']}': Poster not in cache, downloading.")
                self.set_placeholder()
                self.download_poster(poster_path)
        else:
            print(f"ShowCard '{self.show_data['title']}': No poster path, setting placeholder.")
            self.set_placeholder()

    def download_poster(self, poster_path):
        worker = ImageDownloader(poster_path)
        worker.signals.download_finished.connect(self.on_download_finished)
        self.threadpool.start(worker)

    def on_download_finished(self, poster_path, image_data):
        print(f"ShowCard '{self.show_data['title']}': Download finished for {poster_path}")
        if poster_path == self.show_data.get('poster_path'):
            save_image_to_cache(poster_path, image_data)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.poster_label.setPixmap(pixmap)

    def set_placeholder(self):
        placeholder = QPixmap(200, 300)
        placeholder.fill(Qt.GlobalColor.gray)
        self.poster_label.setPixmap(placeholder)

class SeasonCard(ClickableQWidget):
    """
    A widget to display season information.
    """
    def __init__(self, show_id, season_data, parent=None):
        super().__init__(parent)
        self.show_id = show_id
        self.season_data = season_data
        self.pixmap = None
        self.threadpool = QThreadPool()
        self.initUI()
        self.fetch_details()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.poster_label = QLabel()
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_placeholder()
        layout.addWidget(self.poster_label)

        self.name_label = QLabel(self.season_data['name'])
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)

    def fetch_details(self):
        season_number_match = re.search(r'\d+', self.season_data['name'])
        if season_number_match:
            season_number = int(season_number_match.group())
            print(f"SeasonCard '{self.season_data['name']}': Fetching details for show {self.show_id}, season {season_number}")
            worker = SeasonDetailsDownloader(self.show_id, season_number)
            worker.signals.season_details_finished.connect(self.on_details_finished)
            self.threadpool.start(worker)

    def on_details_finished(self, season_details):
        print(f"SeasonCard '{self.season_data['name']}': Details finished.")
        self.season_data['poster_path'] = season_details.get('poster_path')
        self.set_poster()

    def set_poster(self):
        poster_path = self.season_data.get('poster_path')
        print(f"SeasonCard '{self.season_data['name']}': Setting poster with path: {poster_path}")
        if poster_path:
            cached_pixmap = get_image_from_cache(poster_path)
            if cached_pixmap:
                print(f"SeasonCard '{self.season_data['name']}': Found poster in cache.")
                self.poster_label.setPixmap(cached_pixmap)
            else:
                print(f"SeasonCard '{self.season_data['name']}': Poster not in cache, downloading.")
                self.download_poster(poster_path)
        else:
            print(f"SeasonCard '{self.season_data['name']}': No poster path, setting placeholder.")
            self.set_placeholder()

    def download_poster(self, poster_path):
        worker = ImageDownloader(poster_path)
        worker.signals.download_finished.connect(self.on_download_finished)
        self.threadpool.start(worker)

    def on_download_finished(self, poster_path, image_data):
        print(f"SeasonCard '{self.season_data['name']}': Download finished for {poster_path}")
        if poster_path == self.season_data.get('poster_path'):
            save_image_to_cache(poster_path, image_data)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.poster_label.setPixmap(pixmap)

    def set_placeholder(self):
        placeholder = QPixmap(200, 300)
        placeholder.fill(Qt.GlobalColor.gray)
        self.poster_label.setPixmap(placeholder)
