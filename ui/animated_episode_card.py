from PyQt6.QtWidgets import QGraphicsProxyWidget, QWidget, QVBoxLayout
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPointF, pyqtProperty
from PyQt6.QtGui import QTransform
from PyQt6.QtCore import Qt

from ui.episode_widgets import EpisodeWidget

class AnimatedEpisodeCard(QGraphicsProxyWidget):
    def __init__(self, episode_data, pixmap_cache):
        super().__init__()
        
        # Create a container widget to hold the card and its styles
        self.container = QWidget()
        self.episode_card = EpisodeWidget(episode_data, pixmap_cache)
        
        # Use a layout to ensure the card fills the container
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.episode_card)
        
        self.setWidget(self.container)
        self.setTransformOriginPoint(self.boundingRect().center())
        self._rotation_y = 0

        # Animations are disabled for now, but the setup remains
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(300)
        self.pos_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.scale_animation = QPropertyAnimation(self, b"scale")
        self.scale_animation.setDuration(300)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.rotation_animation = QPropertyAnimation(self, b"rotationY")
        self.rotation_animation.setDuration(300)
        self.rotation_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    @pyqtProperty(float)
    def rotationY(self):
        return self._rotation_y

    @rotationY.setter
    def rotationY(self, angle):
        self._rotation_y = angle
        transform = QTransform()
        transform.rotate(self._rotation_y, Qt.Axis.YAxis)
        self.setTransform(transform)

    def animate_to(self, pos, scale, opacity, rotation):
        # This method is kept for potential future use, but we'll use instant set for now
        pass

    def set_properties_instantly(self, pos, scale, opacity, rotation):
        self.setPos(pos)
        self.setScale(scale)
        self.setOpacity(opacity)
        self.rotationY = rotation # Use the property setter

    def set_selected(self, selected):
        if selected:
            self.setZValue(1)
            # Apply style to the container
            self.container.setStyleSheet("background-color: #2a2a2a; border: 3px solid #0090ff; border-radius: 8px;")
        else:
            self.setZValue(0)
            # Apply style to the container
            self.container.setStyleSheet("background-color: #1e1e1e; border: 2px solid #444; border-radius: 8px;")
