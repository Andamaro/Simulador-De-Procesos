from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from app.utils.paths import resource_path
from .theme import BODY


def load_fonts(app: QApplication) -> None:
    for f in sorted(resource_path("assets/fonts").glob("*.ttf")):
        QFontDatabase.addApplicationFont(str(f))
    base = QFont(BODY, 10)
    base.setFamilies([BODY, "Segoe UI Variable Text", "Segoe UI"])
    app.setFont(base)


def font(family: str, px: int, weight=QFont.Weight.Normal, tabular=False) -> QFont:
    f = QFont(family)
    f.setPixelSize(px)
    f.setWeight(weight)
    if tabular and hasattr(f, "setFeature"):
        f.setFeature("tnum", 1)
    return f
