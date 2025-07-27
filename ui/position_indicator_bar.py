from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtCore import Qt

class PositionIndicatorBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.position = 0
        self.total_items = 1

    def set_position(self, position, total_items):
        self.position = position
        self.total_items = total_items
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Bar background
        bar_color = QColor("#333")
        painter.setBrush(QBrush(bar_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 5, 5)

        # Indicator
        if self.total_items > 0:
            bar_width = self.width()
            indicator_width = bar_width / self.total_items
            indicator_x = self.position * indicator_width

            # Ensure the indicator doesn't draw outside the bar due to rounding
            if self.position == self.total_items - 1:
                indicator_width = bar_width - indicator_x
            
            indicator_color = QColor("#0090ff")
            painter.setBrush(QBrush(indicator_color))
            painter.drawRoundedRect(int(indicator_x), 0, int(indicator_width), self.height(), 5, 5)
