from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget

class VideoPlayer(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.setWindowTitle("Codex Video Player")
        self.setGeometry(100, 100, 800, 600)

        self.media_player = QMediaPlayer(self)
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        self.setLayout(layout)

        self.media_player.setSource(video_path)
        self.media_player.play()
