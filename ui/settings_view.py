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

        # Removed Browse Button as per user request (keyboard navigation only)
        layout.addLayout(media_path_layout)

        # Removed Back Button as per user request (keyboard navigation only)

    def browse_media_path(self):
        media_path = QFileDialog.getExistingDirectory(self, 'Select Media Directory')
        if media_path:
            save_media_path(media_path)
            self.media_path_label.setText(f"Media Path: {media_path}")
            self.main_app.scan_and_display_media(media_path)
