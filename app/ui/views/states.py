from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSlider, QVBoxLayout,
                               QWidget)

from app.data.estados import PLANIFICACION, STEPS
from app.ui import theme
from app.ui.widgets.glass import GlassPanel
from app.ui.widgets.statediagram import StateDiagram

SEGUNDOS_POR_PASO = 3.0


class StatesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.idx = 0
        self.timer = QTimer(self)
        self.timer.setInterval(int(SEGUNDOS_POR_PASO * 1000))
        self.timer.timeout.connect(self._auto)
        self.colors = {n: theme.PROC_COLORS[i] for i, n in enumerate("ABC")}
        self._build()
        self.go(0, animate=False)

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.viewport().setAutoFillBackground(False)
        outer.addWidget(scroll)
        inner = QWidget()
        inner.setMinimumSize(900, 640)
        scroll.setWidget(inner)
        root = QVBoxLayout(inner)
        root.setContentsMargins(0, 0, 4, 0)
        root.setSpacing(14)

        head = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(2)
        h1 = QLabel("Estados de los procesos")
        h1.setObjectName("h1")
        sub = QLabel("Modelo de siete estados. Las líneas ámbar son las transiciones del paso actual.")
        sub.setObjectName("muted")
        titles.addWidget(h1)
        titles.addWidget(sub)
        head.addLayout(titles)
        head.addStretch()
        badge = QLabel(PLANIFICACION)
        badge.setStyleSheet("border: 1px solid rgba(255,255,255,0.18); border-radius: 12px; padding: 5px 14px;")
        head.addWidget(badge, 0, Qt.AlignTop)
        root.addLayout(head)

        sheet = GlassPanel()
        sl = QVBoxLayout(sheet)
        sl.setContentsMargins(20, 14, 20, 16)
        sl.setSpacing(10)
        self.diagram = StateDiagram()
        sl.addWidget(self.diagram, 1)
        line = QFrame()
        line.setObjectName("hair")
        line.setFixedHeight(1)
        sl.addWidget(line)

        cap = QHBoxLayout()
        self.counter = QLabel("")
        self.counter.setObjectName("muted")
        self.step_title = QLabel("")
        self.step_title.setObjectName("h2")
        cap.addWidget(self.counter)
        cap.addSpacing(10)
        cap.addWidget(self.step_title)
        cap.addStretch()
        sl.addLayout(cap)
        self.text = QLabel("")
        self.text.setWordWrap(True)
        self.text.setMinimumHeight(48)
        self.text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        sl.addWidget(self.text)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, len(STEPS) - 1)
        self.slider.setPageStep(1)
        self.slider.valueChanged.connect(lambda v: (self.timer.stop(), self._sync_play(), self.go(v)))
        sl.addWidget(self.slider)
        ctl = QHBoxLayout()
        self.btn_reset = QPushButton("Reiniciar")
        self.btn_prev = QPushButton("Anterior")
        self.btn_play = QPushButton("Reproducir")
        self.btn_play.setObjectName("primary")
        self.btn_next = QPushButton("Siguiente")
        for b in (self.btn_reset, self.btn_prev, self.btn_play, self.btn_next):
            b.setMinimumWidth(b.fontMetrics().horizontalAdvance(b.text()) + 36)
            ctl.addWidget(b)
        ctl.addStretch()
        self.btn_reset.clicked.connect(lambda: (self.timer.stop(), self._sync_play(), self.go(0)))
        self.btn_prev.clicked.connect(lambda: (self.timer.stop(), self._sync_play(), self.go(self.idx - 1)))
        self.btn_next.clicked.connect(lambda: (self.timer.stop(), self._sync_play(), self.go(self.idx + 1)))
        self.btn_play.clicked.connect(self.toggle)
        sl.addLayout(ctl)
        root.addWidget(sheet, 1)

    def go(self, i: int, animate: bool = True):
        i = max(0, min(i, len(STEPS) - 1))
        self.idx = i
        s = STEPS[i]
        self.diagram.set_step(s["lists"], s["edges"], self.colors, animate)
        self.counter.setText(f"Paso {i + 1} de {len(STEPS)}")
        self.step_title.setText(s["title"])
        self.text.setText(s["text"])
        self.slider.blockSignals(True)
        self.slider.setValue(i)
        self.slider.blockSignals(False)

    def _sync_play(self):
        self.btn_play.setText("Pausar" if self.timer.isActive() else "Reproducir")

    def toggle(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            if self.idx >= len(STEPS) - 1:
                self.go(0)
            self.timer.start()
        self._sync_play()

    def _auto(self):
        if self.idx >= len(STEPS) - 1:
            self.timer.stop()
        else:
            self.go(self.idx + 1)
        self._sync_play()
