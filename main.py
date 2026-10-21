import sys

from PySide6.QtWidgets import QApplication

from app.ui import theme
from app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    theme.load_fonts()
    app.setFont(theme.body_font())
    app.setStyleSheet(theme.QSS)
    win = MainWindow()
    win.showMaximized()          # inicia maximizada
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
