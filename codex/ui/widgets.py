import requests
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class MediaCard(QWidget):
    """
    A widget to display media information in a card format.
    It will show a poster, title, and release year.
    """
    def __init__(self, title, year, poster_path=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.year = year
        self.poster_path = poster_path
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Poster
        self.poster_label = QLabel()
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_poster()
        layout.addWidget(self.poster_label)

        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Year
        self.year_label = QLabel(str(self.year))
        self.year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.year_label)

    def set_poster(self):
        if self.poster_path:
            try:
                # Construct the full URL
                image_url = f"https://image.tmdb.org/t/p/w200{self.poster_path}"
                response = requests.get(image_url, stream=True)
                response.raise_for_status()
                
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.poster_label.setPixmap(pixmap)
            except requests.exceptions.RequestException as e:
                print(f"Error downloading poster: {e}")
                self.set_placeholder()
        else:
            self.set_placeholder()

    def set_placeholder(self):
        placeholder = QPixmap(200, 300)
        placeholder.fill(Qt.GlobalColor.gray)
        self.poster_label.setPixmap(placeholder)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # Example usage with a poster path
    card = MediaCard("Inception", 2010, "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg")
    card.show()
    sys.exit(app.exec())
