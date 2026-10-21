from PySide6.QtCore import QRectF, Qt, QSize
from PySide6.QtGui import QColor, QFontMetrics, QPainter
from PySide6.QtWidgets import QWidget

from app.ui import theme


class ChipRow(QWidget):
    """Fila de fichas con el nombre de cada proceso."""

    def __init__(self, size: int = 34, parent=None):
        super().__init__(parent)
        self.size = size
        self.items: list[tuple[str, QColor]] = []
        self.empty_text = "vacía"
        self.setFixedHeight(size + 6)

    def set_items(self, items, empty_text: str = "vacía") -> None:
        self.items = list(items)
        self.empty_text = empty_text
        self.update()

    def sizeHint(self):
        return QSize(200, self.size + 6)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        y = (self.height() - self.size) / 2
        if not self.items:
            p.setFont(theme.body_font(10.5))
            p.setPen(QColor(theme.MIST))
            p.drawText(QRectF(0, y, self.width(), self.size), Qt.AlignVCenter | Qt.AlignLeft, self.empty_text)
            return
        p.setFont(theme.display_font(self.size * 0.30))
        x = 0.0
        for name, color in self.items:
            fm = QFontMetrics(p.font())
            w = max(self.size, fm.horizontalAdvance(name) + 18)
            rect = QRectF(x, y, w, self.size)
            p.setPen(Qt.NoPen)
            p.setBrush(color)
            p.drawRoundedRect(rect, 6, 6)
            p.setPen(QColor(theme.INK))
            p.drawText(rect, Qt.AlignCenter, name)
            x += w + 6
            if x > self.width():
                break
