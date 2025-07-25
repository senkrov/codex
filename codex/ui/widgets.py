import requests
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRectF

class MediaCard(QWidget):
    """
    A widget to display media information in a card format.
    It will show a poster with title and year overlaid.
    """
    def __init__(self, title, year, poster_path=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.year = year
        self.poster_path = poster_path
        self.pixmap = None
        self.set_poster()

    def set_poster(self):
        if self.poster_path:
            try:
                image_url = f"https://image.tmdb.org/t/p/w200{self.poster_path}"
                response = requests.get(image_url, stream=True)
                response.raise_for_status()
                
                self.pixmap = QPixmap()
                self.pixmap.loadFromData(response.content)
            except requests.exceptions.RequestException as e:
                print(f"Error downloading poster: {e}")
                self.set_placeholder()
        else:
            self.set_placeholder()
        self.update() # Trigger a repaint

    def set_placeholder(self):
        self.pixmap = QPixmap(200, 300)
        self.pixmap.fill(Qt.GlobalColor.gray)

    def paintEvent(self, event):
        if not self.pixmap:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the poster
        painter.drawPixmap(self.rect(), self.pixmap)

        # Draw the overlay
        overlay_height = 60
        overlay_rect = QRectF(0, self.height() - overlay_height, self.width(), overlay_height)
        
        path = QPainterPath()
        path.addRoundedRect(overlay_rect, 10, 10)
        
        painter.setBrush(QBrush(QColor(0, 0, 0, 180))) # Semi-transparent black
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)

        # Draw the text
        painter.setPen(Qt.GlobalColor.white)
        
        # Title
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        painter.setFont(title_font)
        painter.drawText(QRectF(10, self.height() - 55, self.width() - 20, 30), Qt.AlignmentFlag.AlignLeft, self.title)

        # Year
        year_font = QFont()
        year_font.setPointSize(10)
        painter.setFont(year_font)
        painter.drawText(QRectF(10, self.height() - 30, self.width() - 20, 20), Qt.AlignmentFlag.AlignLeft, str(self.year))

    def sizeHint(self):
        return self.pixmap.size() if self.pixmap else QWidget.sizeHint(self)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # Example usage with a poster path
    card = MediaCard("Inception", 2010, "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg")
    card.show()
    sys.exit(app.exec())
