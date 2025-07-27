from PyQt6.QtWidgets import QGraphicsProxyWidget
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPointF, pyqtProperty
from PyQt6.QtGui import QTransform
from PyQt6.QtCore import Qt

from ui.show_widgets import SeasonCard

class AnimatedSeasonCard(QGraphicsProxyWidget):
    def __init__(self, show_id, season_data, pixmap_cache):
        super().__init__()
        self.season_card = SeasonCard(show_id, season_data, pixmap_cache)
        self.setWidget(self.season_card)
        self.setTransformOriginPoint(self.boundingRect().center())
        self._rotation_y = 0

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
        self.pos_animation.stop()
        self.scale_animation.stop()
        self.opacity_animation.stop()
        self.rotation_animation.stop()

        self.pos_animation.setEndValue(pos)
        self.scale_animation.setEndValue(scale)
        self.opacity_animation.setEndValue(opacity)
        self.rotation_animation.setEndValue(rotation)

        self.pos_animation.start()
        self.scale_animation.start()
        self.opacity_animation.start()
        self.rotation_animation.start()

    def set_selected(self, selected):
        if selected:
            self.setZValue(1)
            self.season_card.setStyleSheet("border: 2px solid #0078D7;")
        else:
            self.setZValue(0)
            self.season_card.setStyleSheet("")

