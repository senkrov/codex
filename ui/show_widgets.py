from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QThreadPool
from cache import get_image_from_cache, save_image_to_cache
from worker import ImageDownloader, WorkerSignals
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
    def __init__(self, show_data, pixmap_cache=None, parent=None):
        super().__init__(parent)
        self.show_data = show_data
        self.pixmap = None
        self.pixmap_cache = pixmap_cache if pixmap_cache is not None else {}
        self.threadpool = QThreadPool()
        self.signals = WorkerSignals()
        self.signals.download_finished.connect(self.on_download_finished)
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
        if poster_path in self.pixmap_cache:
            self.poster_label.setPixmap(self.pixmap_cache[poster_path])
        elif poster_path:
            cached_pixmap = get_image_from_cache(poster_path)
            if cached_pixmap:
                self.pixmap_cache[poster_path] = cached_pixmap
                self.poster_label.setPixmap(cached_pixmap)
            else:
                self.set_placeholder()
                self.download_poster(poster_path)
        else:
            self.set_placeholder()

    def download_poster(self, poster_path):
        worker = ImageDownloader(poster_path, self.signals)
        self.threadpool.start(worker)

    def on_download_finished(self, poster_path, image_data):
        if poster_path == self.show_data.get('poster_path'):
            save_image_to_cache(poster_path, image_data)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.pixmap_cache[poster_path] = pixmap
            self.poster_label.setPixmap(pixmap)

    def set_placeholder(self):
        placeholder = QPixmap(200, 300)
        placeholder.fill(Qt.GlobalColor.gray)
        self.poster_label.setPixmap(placeholder)

class SeasonCard(ClickableQWidget):
    """
    A widget to display season information.
    """
    def __init__(self, show_id, season_data, pixmap_cache=None, parent=None):
        super().__init__(parent)
        self.season_data = season_data
        self.pixmap = None
        self.pixmap_cache = pixmap_cache if pixmap_cache is not None else {}
        self.threadpool = QThreadPool()
        self.signals = WorkerSignals()
        self.signals.download_finished.connect(self.on_download_finished)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.poster_label = QLabel()
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_poster()
        layout.addWidget(self.poster_label)

        self.name_label = QLabel(self.season_data['name'])
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)

    def set_poster(self):
        poster_path = self.season_data.get('poster_path')
        if poster_path in self.pixmap_cache:
            self.poster_label.setPixmap(self.pixmap_cache[poster_path])
        elif poster_path:
            cached_pixmap = get_image_from_cache(poster_path)
            if cached_pixmap:
                self.pixmap_cache[poster_path] = cached_pixmap
                self.poster_label.setPixmap(cached_pixmap)
            else:
                self.download_poster(poster_path)
        else:
            self.set_placeholder()

    def download_poster(self, poster_path):
        worker = ImageDownloader(poster_path, self.signals)
        self.threadpool.start(worker)

    def on_download_finished(self, poster_path, image_data):
        if poster_path == self.season_data.get('poster_path'):
            save_image_to_cache(poster_path, image_data)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.pixmap_cache[poster_path] = pixmap
            self.poster_label.setPixmap(pixmap)

    def set_placeholder(self):
        placeholder = QPixmap(200, 300)
        placeholder.fill(Qt.GlobalColor.gray)
        self.poster_label.setPixmap(placeholder)
