import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit
from scanner import scan_media

class Codex(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Codex')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.results_text = QTextEdit(self)
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        scan_button = QPushButton('Scan Media Directory', self)
        scan_button.clicked.connect(self.scan_directory)
        layout.addWidget(scan_button)

        self.setLayout(layout)

    def scan_directory(self):
        media_path = QFileDialog.getExistingDirectory(self, 'Select Media Directory')
        if media_path:
            movies, shows = scan_media(media_path)
            
            results = "Movies found:\n"
            for movie in movies:
                results += f"  - {movie['title']} ({movie['year']})\n"
            
            results += "\nShows found:\n"
            for show in shows:
                results += f"  - {show['title']}\n"
                for season in show['seasons']:
                    results += f"    - {season['name']} ({len(season['episodes'])} episodes)\n"
            
            self.results_text.setText(results)

def main():
    app = QApplication(sys.argv)
    codex = Codex()
    codex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
