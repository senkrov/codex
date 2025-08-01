from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QThreadPool
from cache import get_image_from_cache, save_image_to_cache
from worker import ImageDownloader, WorkerSignals

class EpisodeWidget(QWidget):
    """
    A widget to display episode information.
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
        self.set_poster()

    def initUI(self):
        self.setFixedSize(200, 112) # Thumbnail size
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0) # Remove internal margins
        
        self.poster_label = QLabel()
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.poster_label)

    def set_poster(self):
        still_path = self.episode_data.get('still_path')
        if still_path in self.pixmap_cache:
            self.pixmap = self.pixmap_cache[still_path]
            self.update_poster()
        elif still_path:
            cached_pixmap = get_image_from_cache(still_path)
            if cached_pixmap:
                self.pixmap = cached_pixmap
                self.pixmap_cache[still_path] = self.pixmap
                self.update_poster()
            else:
                self.set_placeholder()
                self.download_poster(still_path)
        else:
            self.set_placeholder()

    def download_poster(self, still_path):
        worker = ImageDownloader(still_path, self.signals)
        self.threadpool.start(worker)

    def on_download_finished(self, still_path, image_data):
        if still_path == self.episode_data.get('still_path'):
            save_image_to_cache(still_path, image_data)
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(image_data)
            self.pixmap_cache[still_path] = self.pixmap
            self.update_poster()

    def update_poster(self):
        scaled_pixmap = self.pixmap.scaled(200, 112, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.poster_label.setPixmap(scaled_pixmap)

    def set_placeholder(self):
        if not self.pixmap:
            self.pixmap = QPixmap(200, 112)
            self.pixmap.fill(Qt.GlobalColor.gray)
        self.update_poster()
