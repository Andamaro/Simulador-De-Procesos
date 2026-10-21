from PySide6.QtGui import QColor, QFont, QFontDatabase

from app.utils.paths import resource_path

INK = "#050505"
BONE = "#ECECEC"
MIST = "#8C8C8C"
SODIUM = "#FFB341"      # solo: cursor de tiempo y acción principal
ALERT = "#FF8A80"

DISPLAY = "Bricolage Grotesque"
BODY = "IBM Plex Sans"
_FALLBACK = "Segoe UI"

# 12 tonos apagados de luminosidad pareja; ninguno cerca del ámbar (25°–55°).
_HUES = [205, 168, 265, 335, 128, 232, 8, 190, 295, 98, 350, 250]
PROC_COLORS = [QColor.fromHslF(h / 360, 0.42, 0.64) for h in _HUES]


def load_fonts() -> None:
    for f in resource_path("assets", "fonts").glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(f))


def display_font(size: float, bold: bool = True) -> QFont:
    f = QFont(DISPLAY)
    f.setFamilies([DISPLAY, _FALLBACK])
    f.setPointSizeF(size)
    f.setBold(bold)
    return f


def body_font(size: float = 10, bold: bool = False) -> QFont:
    f = QFont(BODY)
    f.setFamilies([BODY, _FALLBACK])
    f.setPointSizeF(size)
    f.setBold(bold)
    return f


QSS = f"""
* {{ color: {BONE}; font-family: "{BODY}", "{_FALLBACK}"; font-size: 10pt; }}
QLabel {{ background: transparent; }}
QLabel#muted {{ color: {MIST}; }}
QLabel#error {{ color: {ALERT}; }}
QLabel#h1 {{ font-family: "{DISPLAY}", "{_FALLBACK}"; font-size: 20pt; font-weight: bold; }}
QLabel#h2:disabled {{ color: rgba(236,236,236,0.30); }}
QLabel#stat {{ font-family: "{DISPLAY}", "{_FALLBACK}"; font-size: 17pt; font-weight: bold; }}
QLabel#bigtitle {{ font-family: "{DISPLAY}", "{_FALLBACK}"; font-size: 22pt; font-weight: bold; }}
QLabel#h2 {{ font-family: "{DISPLAY}", "{_FALLBACK}"; font-size: 12pt; font-weight: bold; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
QFrame#railframe {{ background: transparent; border-right: 1px solid rgba(255,255,255,0.09); }}
QFrame#hair {{ background: rgba(255,255,255,0.09); border: none; }}

QPushButton {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.14);
  border-radius: 6px; padding: 6px 12px; }}
QPushButton:hover {{ background: rgba(255,255,255,0.10); }}
QPushButton:pressed {{ background: rgba(255,255,255,0.16); }}
QPushButton:disabled {{ color: rgba(236,236,236,0.30); border-color: rgba(255,255,255,0.06); }}
QPushButton:focus {{ border: 1px solid {BONE}; }}
QPushButton#primary {{ background: {SODIUM}; color: {INK}; border: 1px solid {SODIUM}; }}
QPushButton#primary:hover {{ background: #FFC265; }}
QPushButton#tab {{ background: transparent; border: none; border-bottom: 2px solid transparent;
  border-radius: 0; padding: 6px 10px; color: {MIST}; }}
QPushButton#tab:hover {{ color: {BONE}; }}
QPushButton#tab:checked {{ color: {BONE}; border-bottom: 2px solid {BONE}; }}
QPushButton#rail {{ text-align: left; background: transparent; border: none;
  border-left: 2px solid transparent; border-radius: 0; padding: 9px 14px; color: {MIST}; }}
QPushButton#rail:hover {{ color: {BONE}; }}
QPushButton#rail:checked {{ color: {BONE}; border-left: 2px solid {BONE}; background: rgba(255,255,255,0.05); }}
QPushButton#step {{ padding: 2px 0; min-width: 26px; max-width: 26px; }}

QSpinBox, QComboBox {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.14);
  border-radius: 6px; padding: 4px 8px; }}
QSpinBox#quantum {{ padding: 0px; min-height: 26px; }}
QSpinBox:disabled {{ color: rgba(236,236,236,0.30); }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{ background: #111111; border: 1px solid rgba(255,255,255,0.18);
  selection-background-color: rgba(255,255,255,0.14); outline: none; }}
QTableWidget {{ background: transparent; border: none; gridline-color: transparent;
  selection-background-color: rgba(255,255,255,0.08); outline: none; }}
QTableWidget::item {{ padding: 4px 6px; border-bottom: 1px solid rgba(255,255,255,0.07); }}
QHeaderView {{ background: transparent; }}
QHeaderView::section {{ background: transparent; color: {MIST}; border: none;
  border-bottom: 1px solid rgba(255,255,255,0.16); padding: 5px 6px; }}
QListWidget {{ background: transparent; border: none; outline: none; }}
QListWidget::item {{ padding: 5px 2px; border-bottom: 1px solid rgba(255,255,255,0.06); }}
QSlider::groove:horizontal {{ height: 3px; background: rgba(255,255,255,0.16); border-radius: 1px; }}
QSlider::sub-page:horizontal {{ background: rgba(236,236,236,0.60); border-radius: 1px; }}
QSlider::handle:horizontal {{ background: {BONE}; width: 12px; height: 12px; margin: -5px 0; border-radius: 6px; }}
QScrollBar:vertical, QScrollBar:horizontal {{ background: transparent; width: 8px; height: 8px; margin: 0; }}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{ background: rgba(255,255,255,0.22);
  border-radius: 4px; min-height: 24px; min-width: 24px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
QCheckBox {{ spacing: 8px; }}
QCheckBox::indicator {{ width: 15px; height: 15px; border: 1px solid rgba(255,255,255,0.40);
  border-radius: 4px; background: transparent; }}
QCheckBox::indicator:checked {{ background: {BONE}; }}
QToolTip {{ background: #111111; color: {BONE}; border: 1px solid rgba(255,255,255,0.22); padding: 4px 6px; }}
"""
