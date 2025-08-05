from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsProxyWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from ui.widgets import MediaCard

class ClickableCategoryCard(QGraphicsProxyWidget):
    clicked = pyqtSignal(str)

    def __init__(self, title, category_type, poster_path=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.category_type = category_type
        
        self.media_card = MediaCard(title=title, poster_path=poster_path, year=None)
        self.setWidget(self.media_card)
        
        self.setCacheMode(self.CacheMode.DeviceCoordinateCache)
        self.setAcceptHoverEvents(False) # Disable hover events

    def mousePressEvent(self, event):
        self.clicked.emit(self.category_type)
        # Pass event to internal widget to ensure it receives the event
        self.media_card.mousePressEvent(event)

    def set_selected(self, selected):
        self.media_card.set_selected(selected)

    def set_properties_instantly(self, pos, scale, opacity, rotation):
        self.setPos(pos)
        self.setScale(scale)
        self.setOpacity(opacity)
        self.setRotation(rotation)