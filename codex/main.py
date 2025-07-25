import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt
from scanner import scan_media
from ui.widgets import MediaCard
from tmdb import TMDbAPI

class Codex(QWidget):
    def __init__(self):
        super().__init__()
        self.tmdb_api = TMDbAPI('1d1f855c79a956515f6438990b93f65b')
        self.cards = []
        self.current_row = 0
        self.current_col = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Codex')
        self.setGeometry(100, 100, 800, 600)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.scroll_area.setWidget(self.grid_container)

        scan_button = QPushButton('Scan Media Directory', self)
        scan_button.clicked.connect(self.scan_directory)
        self.main_layout.addWidget(scan_button)

    def scan_directory(self):
        media_path = QFileDialog.getExistingDirectory(self, 'Select Media Directory')
        if media_path:
            for card in self.cards:
                card.setParent(None)
            self.cards = []
            
            movies, _ = scan_media(media_path)
            
            row, col = 0, 0
            for movie in movies:
                poster_path = None
                search_results = self.tmdb_api.search_movie(movie['title'], movie['year'])
                if search_results and search_results['results']:
                    poster_path = search_results['results'][0].get('poster_path')

                card = MediaCard(movie['title'], movie['year'], poster_path)
                self.grid_layout.addWidget(card, row, col)
                self.cards.append(card)
                col += 1
                if col > 3:
                    col = 0
                    row += 1
            
            self.update_selection()

    def keyPressEvent(self, event):
        key = event.key()
        
        if not self.cards:
            return

        rows = self.grid_layout.rowCount()
        cols = self.grid_layout.columnCount()

        if key == Qt.Key.Key_Right:
            self.current_col = min(self.current_col + 1, cols - 1)
        elif key == Qt.Key.Key_Left:
            self.current_col = max(self.current_col - 1, 0)
        elif key == Qt.Key.Key_Down:
            self.current_row = min(self.current_row + 1, rows - 1)
        elif key == Qt.Key.Key_Up:
            self.current_row = max(self.current_row - 1, 0)
        
        self.update_selection()

    def update_selection(self):
        for i, card in enumerate(self.cards):
            row, col, _, _ = self.grid_layout.getItemPosition(i)
            if row == self.current_row and col == self.current_col:
                card.setStyleSheet("border: 2px solid red;")
            else:
                card.setStyleSheet("")

def main():
    app = QApplication(sys.argv)
    codex = Codex()
    codex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
