from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

class ClickableCategoryCard(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, title, category_type, parent=None):
        super().__init__(parent)
        self.title = title
        self.category_type = category_type # 'movies' or 'shows'
        self.initUI()

    def initUI(self):
        self.setFixedSize(200, 200) # Fixed size for category cards
        self.setStyleSheet("background-color: #333; border: 2px solid #555; border-radius: 10px;")

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel()
        # Placeholder icon, could be replaced with actual icons later
        placeholder = QPixmap(100, 100)
        placeholder.fill(Qt.GlobalColor.darkGray)
        self.icon_label.setPixmap(placeholder)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

    def mousePressEvent(self, event):
        self.clicked.emit(self.category_type)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.setStyleSheet("background-color: #444; border: 2px solid red; border-radius: 10px;")

    def leaveEvent(self, event):
        self.setStyleSheet("background-color: #333; border: 2px solid #555; border-radius: 10px;")
