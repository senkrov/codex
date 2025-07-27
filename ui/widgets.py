from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QThreadPool
from cache import get_image_from_cache, save_image_to_cache
from worker import ImageDownloader, WorkerSignals

class ClickableQWidget(QWidget):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class MediaCard(ClickableQWidget):
    """
    A widget to display media information in a card format.
    """
    def __init__(self, title, year, poster_path=None, pixmap_cache=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.year = year
        self.poster_path = poster_path
        self.pixmap = None
        self.pixmap_cache = pixmap_cache if pixmap_cache is not None else {}
        self.threadpool = QThreadPool()
        self.signals = WorkerSignals()
        self.signals.download_finished.connect(self.on_download_finished)
        self.initUI()
        self.set_poster()

    def initUI(self):
        self.setFixedSize(200, 350)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.poster_label = QLabel()
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.poster_label)

        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        self.year_label = QLabel(str(self.year))
        self.year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.year_label)

    def set_poster(self):
        if self.poster_path in self.pixmap_cache:
            self.pixmap = self.pixmap_cache[self.poster_path]
            self.update_poster()
        elif self.poster_path:
            cached_pixmap = get_image_from_cache(self.poster_path)
            if cached_pixmap:
                self.pixmap = cached_pixmap
                self.pixmap_cache[self.poster_path] = self.pixmap
                self.update_poster()
            else:
                self.set_placeholder()
                self.download_poster()
        else:
            self.set_placeholder()

    def download_poster(self):
        worker = ImageDownloader(self.poster_path, self.signals)
        self.threadpool.start(worker)

    def on_download_finished(self, poster_path, image_data):
        if poster_path == self.poster_path:
            save_image_to_cache(poster_path, image_data)
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(image_data)
            self.pixmap_cache[poster_path] = self.pixmap
            self.update_poster()

    def update_poster(self):
        scaled_pixmap = self.pixmap.scaled(200, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.poster_label.setPixmap(scaled_pixmap)

    def set_placeholder(self):
        if not self.pixmap:
            self.pixmap = QPixmap(200, 300)
            self.pixmap.fill(Qt.GlobalColor.gray)
        self.update_poster()
