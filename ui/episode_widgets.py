from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QThreadPool
from cache import get_image_from_cache, save_image_to_cache
from worker import ImageDownloader, WorkerSignals

class EpisodeWidget(QWidget):
    """
    A widget to display episode information in a card format.
    """
    def __init__(self, episode_data, pixmap_cache=None, parent=None):
        super().__init__(parent)
        self.episode_data = episode_data
        self.pixmap = None
        self.pixmap_cache = pixmap_cache if pixmap_cache is not None else {}
        self.threadpool = QThreadPool()
        self.signals = WorkerSignals()
        self.signals.download_finished.connect(self.on_download_finished)
        self.initUI()
        self.set_thumbnail()

    def initUI(self):
        self.setFixedSize(300, 220)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.thumbnail_label)

        self.title_label = QLabel(f"Episode {self.episode_data.get('episode_number')}: {self.episode_data.get('name')}")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

    def set_thumbnail(self):
        still_path = self.episode_data.get('still_path')
        if still_path in self.pixmap_cache:
            self.pixmap = self.pixmap_cache[still_path]
            self.update_thumbnail()
        elif still_path:
            cached_pixmap = get_image_from_cache(still_path)
            if cached_pixmap:
                self.pixmap = cached_pixmap
                self.pixmap_cache[still_path] = self.pixmap
                self.update_thumbnail()
            else:
                self.set_placeholder()
                self.download_thumbnail(still_path)
        else:
            self.set_placeholder()

    def download_thumbnail(self, still_path):
        worker = ImageDownloader(still_path, self.signals)
        self.threadpool.start(worker)

    def on_download_finished(self, still_path, image_data):
        if still_path == self.episode_data.get('still_path'):
            save_image_to_cache(still_path, image_data)
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(image_data)
            self.pixmap_cache[still_path] = self.pixmap
            self.update_thumbnail()

    def update_thumbnail(self):
        scaled_pixmap = self.pixmap.scaled(300, 170, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.thumbnail_label.setPixmap(scaled_pixmap)

    def set_placeholder(self):
        if not self.pixmap:
            self.pixmap = QPixmap(300, 170)
            self.pixmap.fill(Qt.GlobalColor.gray)
        self.update_thumbnail()
