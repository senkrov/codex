import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QScrollArea, QGridLayout)
from scanner import scan_media
from ui.widgets import MediaCard
from tmdb import TMDbAPI

class Codex(QWidget):
    def __init__(self):
        super().__init__()
        # It's better to get the API key from a secure place
        # For now, we'll use the one from the tmdb.py test
        self.tmdb_api = TMDbAPI('1d1f855c79a956515f6438990b93f65b')
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Codex')
        self.setGeometry(100, 100, 800, 600)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Create a scroll area for the media grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)

        # Create a widget to hold the grid layout
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.scroll_area.setWidget(self.grid_container)

        # Add a scan button
        scan_button = QPushButton('Scan Media Directory', self)
        scan_button.clicked.connect(self.scan_directory)
        self.main_layout.addWidget(scan_button)

    def scan_directory(self):
        media_path = QFileDialog.getExistingDirectory(self, 'Select Media Directory')
        if media_path:
            # Clear existing widgets
            for i in reversed(range(self.grid_layout.count())): 
                self.grid_layout.itemAt(i).widget().setParent(None)

            movies, _ = scan_media(media_path)
            
            # Populate the grid with media cards
            row, col = 0, 0
            for movie in movies:
                poster_path = None
                # Search for the movie on TMDb
                search_results = self.tmdb_api.search_movie(movie['title'], movie['year'])
                if search_results and search_results['results']:
                    poster_path = search_results['results'][0].get('poster_path')

                card = MediaCard(movie['title'], movie['year'], poster_path)
                self.grid_layout.addWidget(card, row, col)
                col += 1
                if col > 3: # Adjust number of columns as needed
                    col = 0
                    row += 1

def main():
    app = QApplication(sys.argv)
    codex = Codex()
    codex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
