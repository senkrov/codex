from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QThreadPool
from cache import get_image_from_cache, save_image_to_cache
from worker import ImageDownloader, WorkerSignals

class EpisodeWidget(QWidget):
    """
    A widget to display episode information in a row format.
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

    def initUI(self):
        self.setFixedHeight(100) # Fixed height for each episode row
        self.setStyleSheet("border: 1px solid #333; border-radius: 5px; margin-bottom: 5px;")

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10) # Add padding
        self.setLayout(layout)

        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(120, 80)
        self.set_thumbnail()
        layout.addWidget(self.thumbnail_label)

        # Episode Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2) # Reduce spacing between labels

        # Title
        self.title_label = QLabel(f"Episode {self.episode_data.get('episode_number')}: {self.episode_data.get('name')}")
        title_font = QFont()
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        info_layout.addWidget(self.title_label)

        # Overview (if available)
        overview = self.episode_data.get('overview')
        if overview:
            self.overview_label = QLabel(overview)
            self.overview_label.setWordWrap(True)
            self.overview_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            info_layout.addWidget(self.overview_label)
        
        layout.addLayout(info_layout)
        layout.addStretch(1) # Push content to the left

    def set_thumbnail(self):
        still_path = self.episode_data.get('still_path')
        if still_path:
            cached_pixmap = self.pixmap_cache.get(still_path)
            if cached_pixmap:
                self.set_pixmap(cached_pixmap)
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
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.pixmap_cache[still_path] = pixmap
            self.set_pixmap(pixmap)

    def set_pixmap(self, pixmap):
        self.thumbnail_label.setPixmap(pixmap.scaled(
            self.thumbnail_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))

    def set_placeholder(self):
        placeholder = QPixmap(self.thumbnail_label.size())
        placeholder.fill(Qt.GlobalColor.gray)
        self.thumbnail_label.setPixmap(placeholder)
