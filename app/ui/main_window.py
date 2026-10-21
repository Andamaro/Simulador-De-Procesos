from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (QCheckBox, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QStackedWidget, QVBoxLayout)

from app.ui.views.performance import PerformanceView
from app.ui.views.simulator import SimulatorView
from app.ui.views.credits import CreditsView
from app.ui.views.glossary import GlossaryView
from app.ui.views.states import StatesView
from app.ui.widgets.glass import Aurora
from app.utils.winfx import set_acrylic

ACRYLIC_ALPHA = 0.82       # casi negro; el blur del escritorio se insinúa


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de procesos — Sistemas Operativos")
        self.setMinimumSize(900, 560)
        self.settings = QSettings("TecNM-ITI", "SimuladorProcesos")
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.bg = Aurora()
        self.setCentralWidget(self.bg)
        lay = QHBoxLayout(self.bg)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        rail = QFrame()
        rail.setObjectName("railframe")
        rail.setFixedWidth(200)
        rl = QVBoxLayout(rail)
        rl.setContentsMargins(0, 22, 0, 16)
        rl.setSpacing(2)
        brand = QLabel("Simulador\nde procesos")
        brand.setObjectName("h2")
        brand.setContentsMargins(16, 0, 0, 0)
        sub = QLabel("Sistemas Operativos\nUnidad 2")
        sub.setObjectName("muted")
        sub.setWordWrap(True)
        sub.setContentsMargins(16, 0, 12, 0)
        rl.addWidget(brand)
        rl.addWidget(sub)
        rl.addSpacing(22)

        self.stack = QStackedWidget()
        self.nav: list[QPushButton] = []
        self.simulator = SimulatorView()
        self.add_view("Simulador", self.simulator, rl)
        self.add_view("Rendimiento", PerformanceView(self.simulator.current_inputs), rl)
        self.add_view("Estados", StatesView(), rl)
        self.add_view("Glosario", GlossaryView(self.show_view), rl)
        self.add_view("Créditos", CreditsView(), rl)
        rl.addStretch()
        self.blur = QCheckBox("Cristal con blur")
        self.blur.setChecked(self.settings.value("blur", True, type=bool))
        self.blur.toggled.connect(self.apply_blur)
        brow = QHBoxLayout()
        brow.setContentsMargins(16, 0, 0, 0)
        brow.addWidget(self.blur)
        rl.addLayout(brow)
        lay.addWidget(rail)

        content = QVBoxLayout()
        content.setContentsMargins(22, 20, 18, 18)
        content.addWidget(self.stack)
        lay.addLayout(content, 1)

    def add_view(self, title: str, widget, rail_layout) -> None:
        idx = self.stack.addWidget(widget)
        b = QPushButton(title)
        b.setObjectName("rail")
        b.setCheckable(True)
        b.setChecked(idx == 0)
        b.clicked.connect(lambda _=False, i=idx: self.show_view(i))
        rail_layout.addWidget(b)
        self.nav.append(b)

    def show_view(self, i: int) -> None:
        self.stack.setCurrentIndex(i)
        view = self.stack.widget(i)
        if hasattr(view, "refresh"):
            view.refresh()
        for j, b in enumerate(self.nav):
            b.setChecked(j == i)

    def apply_blur(self, enabled: bool) -> None:
        ok = set_acrylic(int(self.winId()), enabled)
        self.bg.set_base_alpha(ACRYLIC_ALPHA if (enabled and ok) else 1.0)
        self.settings.setValue("blur", enabled)

    def showEvent(self, e):
        super().showEvent(e)
        if not getattr(self, "_fx_applied", False):
            self._fx_applied = True
            self.apply_blur(self.blur.isChecked())
