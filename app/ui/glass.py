"""Cristal: panel tintado y acrylic de Windows 11 (con respaldo pintado)."""
import sys

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget


def set_backdrop(hwnd: int, acrylic: bool) -> bool:
    """Activa o quita el acrylic del sistema. Devuelve True si Windows lo aceptó."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        from ctypes import wintypes

        dwm = ctypes.windll.dwmapi
        h = wintypes.HWND(hwnd)

        class MARGINS(ctypes.Structure):
            _fields_ = [(n, ctypes.c_int) for n in ("l", "r", "t", "b")]

        dark = ctypes.c_int(1)
        dwm.DwmSetWindowAttribute(h, 20, ctypes.byref(dark), 4)       # modo oscuro
        m = MARGINS(-1, -1, -1, -1) if acrylic else MARGINS(0, 0, 0, 0)
        dwm.DwmExtendFrameIntoClientArea(h, ctypes.byref(m))
        kind = ctypes.c_int(3 if acrylic else 1)                      # 3 = acrylic, 1 = ninguno
        return dwm.DwmSetWindowAttribute(h, 38, ctypes.byref(kind), 4) == 0
    except Exception:
        return False


class GlassPanel(QWidget):
    def __init__(self, radius: int = 18, parent=None):
        super().__init__(parent)
        self.radius = radius

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        g = QLinearGradient(r.topLeft(), r.bottomLeft())
        g.setColorAt(0, QColor(44, 56, 120, 120))
        g.setColorAt(1, QColor(20, 26, 66, 118))
        p.setBrush(g)
        p.setPen(QPen(QColor(255, 255, 255, 34), 1))
        p.drawRoundedRect(r, self.radius, self.radius)
        hl = QLinearGradient(r.left(), 0, r.right(), 0)
        hl.setColorAt(0, QColor(255, 255, 255, 0))
        hl.setColorAt(0.5, QColor(255, 255, 255, 70))
        hl.setColorAt(1, QColor(255, 255, 255, 0))
        p.setPen(QPen(hl, 1))
        p.drawLine(QPointF(r.left() + self.radius, r.top() + 1), QPointF(r.right() - self.radius, r.top() + 1))


BLOBS = [(0.12, 0.08, 0.55, "#2B3A9E", 120), (0.92, 0.9, 0.6, "#1D6B60", 85),
         (0.72, 0.04, 0.38, "#5B2A86", 75)]


def paint_aurora(p: QPainter, w: int, h: int, base_alpha: int) -> None:
    p.fillRect(0, 0, w, h, QColor(10, 13, 28, base_alpha))
    for fx, fy, fr, col, a in BLOBS:
        c = QColor(col)
        g = QRadialGradient(QPointF(fx * w, fy * h), fr * max(w, h))
        c.setAlpha(a)
        g.setColorAt(0, c)
        c.setAlpha(0)
        g.setColorAt(1, c)
        p.fillRect(0, 0, w, h, g)
