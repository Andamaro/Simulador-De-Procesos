from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QFrame, QWidget

from app.ui import theme


class Aurora(QWidget):
    """Fondo negro con un resplandor neutro muy leve. Con acrylic activo la base
    se hace algo translúcida para que se vea el desenfoque del escritorio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_alpha = 1.0

    def set_base_alpha(self, a: float) -> None:
        self.base_alpha = a
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        w, h = self.width(), self.height()
        base = QColor(theme.INK)
        base.setAlphaF(self.base_alpha)
        p.setCompositionMode(QPainter.CompositionMode_Source)
        p.fillRect(self.rect(), base)
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        for fx, fy, fr, a in ((0.08, 0.0, 0.55, 0.075), (1.0, 1.0, 0.45, 0.04)):
            g = QRadialGradient(QPointF(fx * w, fy * h), fr * max(w, h))
            g.setColorAt(0, QColor(255, 255, 255, int(255 * a)))
            g.setColorAt(1, QColor(255, 255, 255, 0))
            p.fillRect(self.rect(), g)


class GlassPanel(QFrame):
    """Hoja de cristal ahumado con borde de luz fino."""

    def __init__(self, parent=None, radius: float = 10):
        super().__init__(parent)
        self.radius = radius

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(r, self.radius, self.radius)
        fill = QLinearGradient(r.topLeft(), r.bottomRight())
        fill.setColorAt(0, QColor(255, 255, 255, 20))
        fill.setColorAt(1, QColor(255, 255, 255, 9))
        p.fillPath(path, fill)
        edge = QLinearGradient(r.topLeft(), r.bottomRight())
        edge.setColorAt(0, QColor(255, 255, 255, 70))
        edge.setColorAt(0.5, QColor(255, 255, 255, 22))
        edge.setColorAt(1, QColor(255, 255, 255, 30))
        p.setPen(QPen(edge, 1))
        p.drawPath(path)
