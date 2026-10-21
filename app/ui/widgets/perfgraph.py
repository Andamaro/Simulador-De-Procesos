import math

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, QVariantAnimation, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from app.ui import theme


def _line_path(values, rect: QRectF, ymax: float, step: bool, upto: float) -> QPainterPath:
    """Camino de la serie hasta la fracción `upto` (0..1) del eje de tiempo."""
    n = len(values) - 1
    path = QPainterPath()
    if n < 1:
        return path
    xs = lambda i: rect.left() + rect.width() * i / n
    ys = lambda v: rect.bottom() - rect.height() * min(v / ymax, 1.0) if ymax else rect.bottom()
    limit = upto * n
    path.moveTo(xs(0), ys(values[0]))
    for i in range(1, n + 1):
        if i - 1 >= limit:
            break
        frac = min(1.0, limit - (i - 1))
        x_end = xs(i - 1) + (xs(i) - xs(i - 1)) * frac
        if step:                                   # el valor se mantiene hasta el siguiente instante
            path.lineTo(x_end, ys(values[i - 1]))
            if frac >= 1.0:
                path.lineTo(xs(i), ys(values[i]))
        else:
            y = ys(values[i - 1] + (values[i] - values[i - 1]) * frac)
            path.lineTo(x_end, y)
    return path


class PerfGraph(QWidget):
    """Gráfica grande al estilo del Administrador de tareas: cuadrícula, línea con
    relleno y borde del color de la serie."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.values: list[float] = []
        self.ymax = 1.0
        self.color = QColor(theme.BONE)
        self.step = False
        self.caption = ""
        self.top_label = ""
        self.value_fmt = lambda v: f"{v:g}"
        self.progress = 1.0
        self.hover: int | None = None
        self.setMouseTracking(True)
        self.setMinimumHeight(220)
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(520)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.valueChanged.connect(self._on_anim)

    def _on_anim(self, v):
        self.progress = float(v)
        self.update()

    def set_data(self, values, ymax, color, step, caption, top_label, value_fmt, animate=True):
        self.values, self.ymax, self.color, self.step = list(values), ymax, QColor(color), step
        self.caption, self.top_label, self.value_fmt = caption, top_label, value_fmt
        self.hover = None
        if animate:
            self.anim.stop()
            self.anim.start()
        else:
            self.progress = 1.0
        self.update()

    def _plot(self) -> QRectF:
        return QRectF(4, 24, self.width() - 8, self.height() - 24 - 24)

    def mouseMoveEvent(self, e):
        r, n = self._plot(), len(self.values) - 1
        if n >= 1 and r.left() <= e.position().x() <= r.right():
            self.hover = round((e.position().x() - r.left()) / r.width() * n)
        else:
            self.hover = None
        self.update()

    def leaveEvent(self, _):
        self.hover = None
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self._plot()
        p.setFont(theme.body_font(9))
        p.setPen(QColor(theme.MIST))
        p.drawText(QRectF(4, 0, self.width() / 2, 20), Qt.AlignLeft | Qt.AlignVCenter, self.caption)
        p.drawText(QRectF(self.width() / 2, 0, self.width() / 2 - 4, 20), Qt.AlignRight | Qt.AlignVCenter, self.top_label)
        p.fillRect(r, QColor(255, 255, 255, 7))
        n = len(self.values) - 1
        if n < 1:
            return
        # cuadrícula: una línea por unidad de tiempo (o cada 2, 5, 10…) y cuatro divisiones en vertical
        step_t = next(s for s in (1, 2, 5, 10, 20, 50, 100) if s * r.width() / n >= 22)
        p.setPen(QPen(QColor(255, 255, 255, 22), 1))
        for t in range(0, n + 1, step_t):
            x = r.left() + r.width() * t / n
            p.drawLine(QPointF(x, r.top()), QPointF(x, r.bottom()))
        for k in range(1, 4):
            y = r.top() + r.height() * k / 4
            p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))
        # relleno y línea
        line = _line_path(self.values, r, self.ymax, self.step, self.progress)
        if line.elementCount() > 1:
            fill = QPainterPath(line)
            end = line.currentPosition()
            fill.lineTo(end.x(), r.bottom())
            fill.lineTo(r.left(), r.bottom())
            fill.closeSubpath()
            g = QLinearGradient(0, r.top(), 0, r.bottom())
            top, bot = QColor(self.color), QColor(self.color)
            top.setAlpha(110)
            bot.setAlpha(14)
            g.setColorAt(0, top)
            g.setColorAt(1, bot)
            p.fillPath(fill, g)
            p.setPen(QPen(self.color, 1.8))
            p.setBrush(Qt.NoBrush)
            p.drawPath(line)
        edge = QColor(self.color)
        edge.setAlpha(170)
        p.setPen(QPen(edge, 1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(r)
        # ejes
        p.setPen(QColor(theme.MIST))
        p.drawText(QRectF(r.left(), r.bottom() + 4, 120, 18), Qt.AlignLeft | Qt.AlignVCenter, "t = 0")
        p.drawText(QRectF(r.right() - 120, r.bottom() + 4, 120, 18), Qt.AlignRight | Qt.AlignVCenter, f"t = {n}")
        # lectura al pasar el mouse
        if self.hover is not None and self.hover / n <= self.progress + 1e-6:
            i = self.hover
            x = r.left() + r.width() * i / n
            y = r.bottom() - r.height() * min(self.values[i] / self.ymax, 1.0) if self.ymax else r.bottom()
            p.setPen(QPen(QColor(theme.SODIUM), 1.5))
            p.drawLine(QPointF(x, r.top()), QPointF(x, r.bottom()))
            p.setBrush(QColor(theme.SODIUM))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(x, y), 4, 4)
            text = f"t = {i}   {self.value_fmt(self.values[i])}"
            w = p.fontMetrics().horizontalAdvance(text) + 18
            bx = min(max(x + 10, r.left()), r.right() - w)
            box = QRectF(bx, r.top() + 8, w, 24)
            p.setBrush(QColor(12, 12, 12, 235))
            p.setPen(QPen(QColor(255, 255, 255, 50), 1))
            p.drawRoundedRect(box, 5, 5)
            p.setPen(QColor(theme.BONE))
            p.drawText(box, Qt.AlignCenter, text)


class AlgoItem(QWidget):
    """Elemento de la barra lateral: miniatura de la serie, nombre y resumen."""
    clicked = Signal(str)

    def __init__(self, key: str, title: str, parent=None):
        super().__init__(parent)
        self.key, self.title = key, title
        self.subtitle = ""
        self.values: list[float] = []
        self.ymax = 1.0
        self.color = QColor(theme.BONE)
        self.step = False
        self.selected = False
        self.setFixedHeight(78)
        self.setCursor(Qt.PointingHandCursor)

    def update_data(self, values, ymax, color, step, subtitle):
        self.values, self.ymax, self.color, self.step, self.subtitle = values, ymax, QColor(color), step, subtitle
        self.update()

    def mousePressEvent(self, e):
        self.clicked.emit(self.key)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if self.selected:
            p.fillRect(self.rect(), QColor(255, 255, 255, 22))
            p.fillRect(QRectF(0, 0, 2, self.height()), QColor(theme.BONE))
        thumb = QRectF(14, 13, 92, 52)
        p.fillRect(thumb, QColor(255, 255, 255, 8))
        line = _line_path(self.values, thumb, self.ymax, self.step, 1.0)
        if line.elementCount() > 1:
            fill = QPainterPath(line)
            end = line.currentPosition()
            fill.lineTo(end.x(), thumb.bottom())
            fill.lineTo(thumb.left(), thumb.bottom())
            fill.closeSubpath()
            c = QColor(self.color)
            c.setAlpha(70)
            p.fillPath(fill, c)
            p.setPen(QPen(self.color, 1.3))
            p.drawPath(line)
        edge = QColor(self.color)
        edge.setAlpha(150)
        p.setPen(QPen(edge, 1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(thumb)
        p.setPen(QColor(theme.BONE))
        p.setFont(theme.display_font(11.5))
        p.drawText(QRectF(120, 14, self.width() - 126, 24), Qt.AlignLeft | Qt.AlignVCenter, self.title)
        p.setPen(QColor(theme.MIST))
        p.setFont(theme.body_font(9))
        p.drawText(QRectF(120, 38, self.width() - 126, 28), Qt.AlignLeft | Qt.TextWordWrap, self.subtitle)
