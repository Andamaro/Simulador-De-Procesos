import math

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, QVariantAnimation, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget

from app.ui import theme

LW, LH = 850.0, 336.0          # espacio lógico del diagrama
SLOT_D = 27.0

# clave: (x, y, ancho, alto, título, ranuras)
BOXES = {
    "NUE": (153, 12, 142, 68, "Nuevo", 3),
    "LSU": (28, 140, 140, 68, "Listo suspendido", 3),
    "LIS": (276, 140, 140, 68, "Listo", 3),
    "EJE": (493, 140, 90, 68, "Ejecutando", 1),
    "SAL": (675, 140, 140, 68, "Saliente", 3),
    "BSU": (28, 255, 140, 68, "Bloqueado suspendido", 3),
    "BLO": (276, 255, 140, 68, "Bloqueado", 3),
}
# clave: (puntos, etiqueta, centro de la etiqueta)
EDGES = {
    "NUE>LSU": ([(185, 80), (125, 140)], "Admisión", (118, 112)),
    "NUE>LIS": ([(262, 80), (320, 140)], "Admisión", (330, 112)),
    "LSU>LIS": ([(168, 158), (276, 158)], "Reactivación", (222, 150)),
    "LIS>LSU": ([(276, 190), (168, 190)], "Suspensión", (222, 200)),
    "LIS>EJE": ([(416, 158), (493, 158)], "Activación", (455, 150)),
    "EJE>LIS": ([(493, 190), (416, 190)], "Fin de quantum", (455, 201)),
    "EJE>SAL": ([(583, 174), (675, 174)], "Salida", (629, 166)),
    "EJE>BLO": ([(520, 208), (416, 268)], "Espera por suceso", (520, 250)),
    "BLO>LIS": ([(345, 255), (345, 208)], "Sucede evento", (392, 232)),
    "BSU>LSU": ([(98, 255), (98, 208)], "Sucede evento", (146, 232)),
    "BSU>BLO": ([(168, 273), (276, 273)], "Reactivación", (222, 265)),
    "BLO>BSU": ([(276, 305), (168, 305)], "Suspensión", (222, 315)),
}


def slot_pos(state: str, i: int) -> QPointF:
    x, y, w, h, _t, n = BOXES[state]
    if n == 1:
        return QPointF(x + w / 2, y + 44)
    return QPointF(x + 30 + i * 40, y + 44)


class StateDiagram(QWidget):
    """Modelo de siete estados. Las transiciones del paso actual se resaltan en ámbar
    y los procesos se deslizan de un estado a otro."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors: dict[str, QColor] = {}
        self.pos: dict[str, QPointF] = {}      # posición dibujada
        self.src: dict[str, QPointF] = {}
        self.dst: dict[str, QPointF] = {}
        self.active: set[str] = set()
        self.setMinimumHeight(250)
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(520)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.anim.valueChanged.connect(self._on_anim)

    def _on_anim(self, v):
        v = float(v)
        for n, d in self.dst.items():
            s = self.src.get(n, d)
            self.pos[n] = QPointF(s.x() + (d.x() - s.x()) * v, s.y() + (d.y() - s.y()) * v)
        self.update()

    def set_step(self, lists: dict, edges, colors, animate: bool = True) -> None:
        self.colors = colors
        self.active = set(edges)
        dst = {}
        for state, names in lists.items():
            for i, n in enumerate(names):
                dst[n] = slot_pos(state, i)
        self.src = dict(self.pos) if animate else dict(dst)
        self.dst = dst
        for n in dst:
            self.src.setdefault(n, dst[n])
        self.anim.stop()
        if animate:
            self.anim.start()
        else:
            self.pos = dict(dst)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        sc = min(self.width() / LW, self.height() / LH)
        p.translate((self.width() - LW * sc) / 2, (self.height() - LH * sc) / 2)
        p.scale(sc, sc)
        small = QFont(theme.BODY)
        small.setPixelSize(10)
        small.setFamilies([theme.BODY, "Segoe UI"])
        for key, (pts, label, (lx, ly)) in EDGES.items():
            on = key in self.active
            col = QColor(theme.SODIUM) if on else QColor(255, 255, 255, 85)
            p.setPen(QPen(col, 2.2 if on else 1.1))
            (x0, y0), (x1, y1) = pts
            p.drawLine(QPointF(x0, y0), QPointF(x1, y1))
            ang = math.atan2(y1 - y0, x1 - x0)
            head = QPolygonF([QPointF(x1, y1),
                              QPointF(x1 - 8 * math.cos(ang - 0.4), y1 - 8 * math.sin(ang - 0.4)),
                              QPointF(x1 - 8 * math.cos(ang + 0.4), y1 - 8 * math.sin(ang + 0.4))])
            p.setBrush(col)
            p.setPen(Qt.NoPen)
            p.drawPolygon(head)
            f = QFont(small)
            f.setBold(on)
            p.setFont(f)
            p.setPen(QColor(theme.SODIUM) if on else QColor(theme.MIST))
            p.drawText(QRectF(lx - 60, ly - 8, 120, 16), Qt.AlignCenter, label)
        title = QFont(theme.DISPLAY)
        title.setFamilies([theme.DISPLAY, "Segoe UI"])
        title.setPixelSize(12)
        title.setBold(True)
        for key, (x, y, w, h, name, n) in BOXES.items():
            r = QRectF(x, y, w, h)
            p.setBrush(QColor(255, 255, 255, 16))
            p.setPen(QPen(QColor(255, 255, 255, 60), 1))
            p.drawRoundedRect(r, 7, 7)
            p.setFont(title)
            p.setPen(QColor(theme.BONE))
            p.drawText(QRectF(x, y + 5, w, 18), Qt.AlignCenter, name)
            p.setBrush(QColor(255, 255, 255, 14))
            p.setPen(QPen(QColor(255, 255, 255, 30), 1))
            for i in range(n):
                c = slot_pos(key, i)
                p.drawEllipse(c, SLOT_D / 2, SLOT_D / 2)
        chip = QFont(theme.DISPLAY)
        chip.setFamilies([theme.DISPLAY, "Segoe UI"])
        chip.setPixelSize(14)
        chip.setBold(True)
        p.setFont(chip)
        for name, c in self.pos.items():
            p.setPen(Qt.NoPen)
            p.setBrush(self.colors.get(name, QColor(theme.BONE)))
            p.drawEllipse(c, SLOT_D / 2, SLOT_D / 2)
            p.setPen(QColor(theme.INK))
            p.drawText(QRectF(c.x() - 14, c.y() - 14, 28, 28), Qt.AlignCenter, name)
