from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QThreadPool
from cache import get_image_from_cache, save_image_to_cache
from worker import ImageDownloader, WorkerSignals

class MediaCard(QWidget):
    """
    A widget to display media information in a card format.
    It will show a poster with title and year overlaid.
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
        self.set_poster()

    def set_poster(self):
        if self.poster_path in self.pixmap_cache:
            self.pixmap = self.pixmap_cache[self.poster_path]
            self.update()
        elif self.poster_path:
            cached_pixmap = get_image_from_cache(self.poster_path)
            if cached_pixmap:
                self.pixmap = cached_pixmap
                self.pixmap_cache[self.poster_path] = self.pixmap
                self.update()
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
            self.update()

    def set_placeholder(self):
        if not self.pixmap:
            self.pixmap = QPixmap(200, 300)
            self.pixmap.fill(Qt.GlobalColor.gray)
        self.update()

    def paintEvent(self, event):
        if not self.pixmap:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(self.rect(), self.pixmap)

        overlay_height = 60
        overlay_rect = QRectF(0, self.height() - overlay_height, self.width(), overlay_height)
        
        path = QPainterPath()
        path.addRoundedRect(overlay_rect, 10, 10)
        
        painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)

        painter.setPen(Qt.GlobalColor.white)
        
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        painter.setFont(title_font)
        painter.drawText(QRectF(10, self.height() - 55, self.width() - 20, 30), Qt.AlignmentFlag.AlignLeft, self.title)

        year_font = QFont()
        year_font.setPointSize(10)
        painter.setFont(year_font)
        painter.drawText(QRectF(10, self.height() - 30, self.width() - 20, 20), Qt.AlignmentFlag.AlignLeft, str(self.year))

    def sizeHint(self):
        return self.pixmap.size() if self.pixmap else QWidget.sizeHint(self)
