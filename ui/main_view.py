from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import pyqtSignal, Qt, QPointF, QTimer
from ui.category_widgets import ClickableCategoryCard

class MainView(QGraphicsView):
    category_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus) # Ensure MainView can receive keyboard focus
        self.initUI()

    def initUI(self):
        self.movies_card = ClickableCategoryCard("Movies", "movies", poster_path="/path/to/movie_placeholder.jpg")
        self.movies_card.clicked.connect(self.category_selected.emit)
        self.scene.addItem(self.movies_card)

        self.shows_card = ClickableCategoryCard("Shows", "shows", poster_path="/path/to/show_placeholder.jpg")
        self.shows_card.clicked.connect(self.category_selected.emit)
        self.scene.addItem(self.shows_card)

        self.podcasts_card = ClickableCategoryCard("Podcasts", "podcasts", poster_path="/path/to/podcast_placeholder.jpg")
        self.scene.addItem(self.podcasts_card)

        self.cards = [self.movies_card, self.shows_card, self.podcasts_card]
        self.current_selection_index = 0
        
        # Initial positioning and selection update
        QTimer.singleShot(10, self.update_card_positions) # Delay to ensure view is ready

    def update_card_positions(self):
        if not self.cards:
            return

        view_width = self.viewport().width()
        card_width = self.cards[0].boundingRect().width()
        num_cards = len(self.cards)

        # Dynamic Focal Point Calculation
        start_x = view_width * 0.15
        end_x = view_width * 0.85
        
        if num_cards > 1:
            focal_point_x = start_x + (self.current_selection_index / (num_cards - 1)) * (end_x - start_x)
        else:
            focal_point_x = view_width / 2

        for i, card in enumerate(self.cards):
            distance = i - self.current_selection_index

            card_spacing = 30
            offset = distance * (card_width * 0.4 + card_spacing)
            pos_x = focal_point_x + offset - (card_width / 2)

            if distance == 0:
                scale = 1.0
                opacity = 1.0
                rotation = 0
                card.set_selected(True)
                card.setZValue(num_cards) # Bring selected card to front
            else:
                scale = 0.8
                opacity = 0.7
                card.set_selected(False)
                card.setZValue(num_cards - abs(distance)) # Order other cards by distance
                
                if distance < 0:
                    rotation = 25
                else:
                    rotation = -25

            card.set_properties_instantly(QPointF(pos_x, 0), scale, opacity, rotation)

    

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_card_positions()