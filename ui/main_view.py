from PyQt6.QtWidgets import QWidget, QGridLayout
from PyQt6.QtCore import pyqtSignal, Qt
from ui.category_widgets import ClickableCategoryCard

class MainView(QWidget):
    category_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.movies_card = ClickableCategoryCard("Movies", "movies")
        self.movies_card.clicked.connect(self.category_selected.emit)
        layout.addWidget(self.movies_card, 0, 0, Qt.AlignmentFlag.AlignCenter)

        self.shows_card = ClickableCategoryCard("Shows", "shows")
        self.shows_card.clicked.connect(self.category_selected.emit)
        layout.addWidget(self.shows_card, 0, 1, Qt.AlignmentFlag.AlignCenter)

        self.podcasts_card = ClickableCategoryCard("Podcasts", "podcasts")
        self.podcasts_card.clicked.connect(self.category_selected.emit)
        layout.addWidget(self.podcasts_card, 0, 2, Qt.AlignmentFlag.AlignCenter)

        self.cards = [self.movies_card, self.shows_card, self.podcasts_card]
        self.current_selection_index = 0
        self.update_selection()

    def update_selection(self):
        for i, card in enumerate(self.cards):
            if i == self.current_selection_index:
                card.setStyleSheet("background-color: #444; border: 2px solid red; border-radius: 10px;")
            else:
                card.setStyleSheet("background-color: #333; border: 2px solid #555; border-radius: 10px;")

    def keyPressEvent(self, event):
        key = event.key()
        
        if key == Qt.Key.Key_Left:
            self.current_selection_index = max(0, self.current_selection_index - 1)
        elif key == Qt.Key.Key_Right:
            self.current_selection_index = min(len(self.cards) - 1, self.current_selection_index + 1)
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Space:
            self.category_selected.emit(self.cards[self.current_selection_index].category_type)
        
        self.update_selection()
