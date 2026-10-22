from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QWidget

from app.core import Result
from app.ui import theme


class GanttWidget(QWidget):
    """Gráfica de Gantt de un solo carril, como la del pizarrón. Las barras se
    encienden a medida que el cursor de tiempo (ámbar) las recorre."""

    LANE_H = 64
    PAD = 28

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result: Result | None = None
        self.colors: dict[str, QColor] = {}
        self.t = 0.0
        self.setMinimumHeight(170)

    def set_result(self, result, colors) -> None:
        self.result, self.colors = result, colors
        self.update()

    def set_time(self, t: float) -> None:
        self.t = t
        self.update()

    def _tick_step(self, scale: float) -> int:
        for step in (1, 2, 5, 10, 20, 50, 100):
            if step * scale >= 26:
                return step
        return 100

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if not self.result or not self.result.segments:
            p.setFont(theme.body_font(11))
            p.setPen(QColor(theme.MIST))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter,
                       "Agrega al menos un proceso en la tabla para ver su gráfica.")
            return
        res, total = self.result, self.result.makespan
        lane_h = max(56.0, min(100.0, h * 0.34))
        left, right = self.PAD, self.PAD
        scale = (w - left - right) / total
        lane_y = max(22.0, (h - lane_h - 78) / 2 + 14)
        axis_y = lane_y + lane_h + 8

        track = QPainterPath()
        track.addRoundedRect(QRectF(left - 4, lane_y - 4, w - left - right + 8, lane_h + 8), 8, 8)
        p.fillPath(track, QColor(255, 255, 255, 10))

        for seg in res.segments:
            x0, x1 = left + seg.start * scale, left + seg.end * scale
            full = QRectF(x0 + 1, lane_y, max(x1 - x0 - 2, 1), lane_h)
            if self.t <= seg.start:                       # aún no recorrido: contorno tenue
                p.setPen(QPen(QColor(255, 255, 255, 40), 1, Qt.DashLine))
                p.setBrush(Qt.NoBrush)
                p.drawRoundedRect(full, 5, 5)
                continue
            reached = min(self.t, seg.end)
            rect = QRectF(full.x(), full.y(), max(left + reached * scale - x0 - 2, 1), full.height())
            p.setPen(Qt.NoPen)
            if seg.overhead:
                p.setBrush(QColor(255, 255, 255, 58))
            elif seg.idle:
                p.setBrush(QColor(255, 255, 255, 22))
            else:
                p.setBrush(self.colors.get(seg.name, QColor(theme.MIST)))
            p.drawRoundedRect(rect, 5, 5)
            label = "cc" if seg.overhead else ("inactiva" if seg.idle else seg.name)
            p.setFont(theme.display_font(15 if not (seg.idle or seg.overhead) else 9.5))
            p.setPen(QColor(theme.MIST if (seg.idle or seg.overhead) else theme.INK))
            if p.fontMetrics().horizontalAdvance(label) + 10 < rect.width():
                p.drawText(rect, Qt.AlignCenter, label)

        if any(x.overhead for x in res.segments):
            p.setFont(theme.body_font(8.5))
            p.setPen(QColor(theme.MIST))
            p.drawText(QRectF(left, 2, w - left - right, 16), Qt.AlignRight | Qt.AlignVCenter, "cc = cambio de contexto")

        # eje de tiempo y anillos en los instantes finales (I_final)
        step = self._tick_step(scale)
        p.setFont(theme.body_font(9))
        finishes = {m.finish: m.name for m in res.metrics}
        near = lambda tick: any(f != tick and abs(f - tick) * scale < 26 for f in finishes)
        last_x, last_row = -999.0, 1
        for tick in range(0, total + 1):
            x = left + tick * scale
            is_fin = tick in finishes
            show = is_fin or tick == total or (tick % step == 0 and not near(tick))
            p.setPen(QPen(QColor(255, 255, 255, 70 if show else 28), 1))
            p.drawLine(QPointF(x, axis_y), QPointF(x, axis_y + (6 if show else 3)))
            if not show:
                continue
            row = 0
            if is_fin:
                row = 1 - last_row if x - last_x < 26 else 0
                last_x, last_row = x, row
            cy = axis_y + 20 + row * 24
            if row:
                p.setPen(QPen(QColor(255, 255, 255, 40), 1))
                p.drawLine(QPointF(x, axis_y + 6), QPointF(x, cy - 10))
            if is_fin and self.t >= tick:
                p.setPen(QPen(self.colors.get(finishes[tick], QColor(theme.BONE)), 2))
                p.setBrush(Qt.NoBrush)
                p.drawEllipse(QPointF(x, cy), 10, 10)
            p.setPen(QColor(theme.BONE if tick <= self.t else theme.MIST))
            p.drawText(QRectF(x - 16, cy - 10, 32, 20), Qt.AlignCenter, str(tick))

        # cursor de tiempo
        cx = left + min(self.t, total) * scale
        glow = QLinearGradient(cx, lane_y - 14, cx, axis_y)
        glow.setColorAt(0, QColor(255, 179, 65, 0))
        glow.setColorAt(0.2, QColor(255, 179, 65, 60))
        glow.setColorAt(1, QColor(255, 179, 65, 0))
        p.fillRect(QRectF(cx - 7, lane_y - 14, 14, axis_y - lane_y + 14), glow)
        p.setPen(QPen(QColor(theme.SODIUM), 2))
        p.drawLine(QPointF(cx, lane_y - 12), QPointF(cx, axis_y))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(theme.SODIUM))
        p.drawPolygon(QPolygonF([QPointF(cx - 6, lane_y - 18), QPointF(cx + 6, lane_y - 18), QPointF(cx, lane_y - 8)]))
