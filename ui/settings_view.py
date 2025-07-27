from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QHBoxLayout
from config import save_media_path, load_media_path

class SettingsView(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Media Path Selection
        media_path_layout = QHBoxLayout()
        self.media_path_label = QLabel(f"Media Path: {load_media_path() or 'Not Set'}")
        media_path_layout.addWidget(self.media_path_label)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_media_path)
        media_path_layout.addWidget(browse_button)
        layout.addLayout(media_path_layout)

        # Back Button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.main_app.show_main_view)
        layout.addWidget(back_button)

    def browse_media_path(self):
        media_path = QFileDialog.getExistingDirectory(self, 'Select Media Directory')
        if media_path:
            save_media_path(media_path)
            self.media_path_label.setText(f"Media Path: {media_path}")
            self.main_app.scan_and_display_media(media_path)
