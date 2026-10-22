from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (QButtonGroup, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
                               QScrollArea, QVBoxLayout, QWidget)

from app.core import ALGORITMOS, fmt, simulate
from app.core.analytics import series, summary
from app.ui import theme
from app.ui.widgets.glass import GlassPanel
from app.ui.widgets.perfgraph import AlgoItem, PerfGraph

NOMBRES = {"FCFS": "FCFS", "SJF": "SJF", "SRTF": "SRTF", "RR": "Round Robin"}
# clave: (título, ¿escalón?, índice de color, formato de lectura, descripción del eje)
METRICAS = {
    "cpu": ("Uso de CPU", False, 1, lambda v: f"{v:.0f} %", "Porcentaje del tiempo dedicado a ejecutar procesos, desde t = 0"),
    "ready": ("Cola de listos", True, 2, lambda v: f"{v:g} en cola", "Procesos esperando CPU en cada instante"),
    "done": ("Procesos terminados", True, 4, lambda v: f"{v:g} terminados", "Procesos que ya terminaron"),
    "wait": ("Espera acumulada", False, 3, lambda v: f"{v:g} unidades", "Suma de la espera de todos los procesos hasta t"),
}


def _nice_ceil(v: float) -> float:
    if v <= 0:
        return 1.0
    for step in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000):
        if v <= step * 4:
            s = step / 2 if step >= 2 and v <= step * 2 else step
            return float(-(-v // s) * s) if s >= 1 else float(-(-v // 1))
    return float(v)


class PerformanceView(QWidget):
    """Compara los cuatro algoritmos con los procesos del Simulador."""

    def __init__(self, get_inputs, parent=None):
        super().__init__(parent)
        self.get_inputs = get_inputs
        self.results: dict = {}
        self.sums: dict = {}
        self.algo = "FCFS"
        self.metric = "cpu"
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.viewport().setAutoFillBackground(False)
        outer.addWidget(scroll)
        inner = QWidget()
        inner.setMinimumSize(980, 640)
        scroll.setWidget(inner)
        root = QVBoxLayout(inner)
        root.setContentsMargins(0, 0, 4, 0)
        root.setSpacing(14)

        h1 = QLabel("Rendimiento")
        h1.setObjectName("h1")
        self.verdict = QLabel("")
        self.verdict.setObjectName("muted")
        root.addWidget(h1)
        root.addWidget(self.verdict)

        self.msg = QLabel("")
        self.msg.setObjectName("error")
        self.msg.setWordWrap(True)
        root.addWidget(self.msg)
        self.msg.setVisible(False)

        self.sheet = GlassPanel()
        sh = QHBoxLayout(self.sheet)
        sh.setContentsMargins(0, 0, 0, 0)
        sh.setSpacing(0)
        root.addWidget(self.sheet, 1)

        side = QWidget()
        side.setFixedWidth(300)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(0, 10, 0, 10)
        sl.setSpacing(0)
        self.items: dict[str, AlgoItem] = {}
        for key in ALGORITMOS:
            it = AlgoItem(key, NOMBRES[key])
            it.clicked.connect(self.select_algo)
            self.items[key] = it
            sl.addWidget(it)
        sl.addStretch()
        sh.addWidget(side)
        line = QFrame()
        line.setObjectName("hair")
        line.setFixedWidth(1)
        sh.addWidget(line)

        main = QWidget()
        ml = QVBoxLayout(main)
        ml.setContentsMargins(22, 16, 22, 16)
        ml.setSpacing(10)
        sh.addWidget(main, 1)

        tabs = QHBoxLayout()
        self.group = QButtonGroup(self)
        for key, (title, *_r) in METRICAS.items():
            b = QPushButton(title)
            b.setObjectName("tab")
            b.setCheckable(True)
            b.setChecked(key == "cpu")
            b.setProperty("metric", key)
            b.setMinimumWidth(QFontMetrics(b.font()).horizontalAdvance(title) + 30)
            self.group.addButton(b)
            tabs.addWidget(b)
        tabs.addStretch()
        self.group.buttonClicked.connect(lambda b: self.select_metric(b.property("metric")))
        ml.addLayout(tabs)

        head = QHBoxLayout()
        self.big_title = QLabel("")
        self.big_title.setObjectName("bigtitle")
        self.big_algo = QLabel("")
        self.big_algo.setObjectName("muted")
        head.addWidget(self.big_title)
        head.addStretch()
        head.addWidget(self.big_algo)
        ml.addLayout(head)

        self.graph = PerfGraph()
        ml.addWidget(self.graph, 1)

        grid = QGridLayout()
        grid.setHorizontalSpacing(28)
        grid.setVerticalSpacing(10)
        self.stat_values: dict[str, QLabel] = {}
        stats = [("utilizacion", "Uso útil de CPU"), ("cambios", "Cambios de contexto"),
                 ("tiempo_cambios", "Tiempo en cambios"), ("cola_maxima", "Cola máxima"),
                 ("tiempo_total", "Tiempo total"), ("t_prom", "T servicio promedio"),
                 ("e_prom", "E espera promedio"), ("i_prom", "I índice promedio"),
                 ("por_unidad", "Procesos por unidad")]
        for i, (key, label) in enumerate(stats):
            cell = QVBoxLayout()
            cell.setSpacing(0)
            cap = QLabel(label)
            cap.setObjectName("muted")
            val = QLabel("—")
            val.setObjectName("stat")
            self.stat_values[key] = val
            cell.addWidget(cap)
            cell.addWidget(val)
            grid.addLayout(cell, i // 5, i % 5)
        ml.addLayout(grid)

    # ------------------------------------------------------------ datos
    def refresh(self):
        procs, quantum, cost, err = self.get_inputs()
        self.msg.setText(err or "")
        self.msg.setVisible(bool(err))
        self.sheet.setVisible(not err)
        if err:
            self.verdict.setText("")
            return
        try:
            self.results = {k: simulate(k, procs, quantum, cost) for k in ALGORITMOS}
        except ValueError as e:
            self.results = {}
            self.msg.setText(f"Corrige la tabla de procesos en el Simulador: {e}")
            self.msg.setVisible(True)
            self.sheet.setVisible(False)
            self.verdict.setText("")
            return
        self.sums = {k: summary(r) for k, r in self.results.items()}
        self.items["RR"].title = f"Round Robin (q = {quantum})"
        best = min(s["e_prom"] for s in self.sums.values())
        winners = [NOMBRES[k] for k, s in self.sums.items() if abs(s["e_prom"] - best) < 1e-9]
        extra = f" Con cambio de contexto de {cost} unidad(es)." if cost else ""
        self.verdict.setText(f"Menor espera promedio con estos procesos: {' y '.join(winners)} ({fmt(best)}).{extra} "
                             "Cambia la tabla o los ajustes en el Simulador y vuelve aquí.")
        self._refresh_graphics(animate=False)

    def _common_ymax(self) -> float:
        if self.metric == "cpu":
            return 100.0
        return _nice_ceil(max(max(series(r, self.metric)) for r in self.results.values()))

    def _refresh_graphics(self, animate: bool):
        title, step, cidx, vfmt, desc = METRICAS[self.metric]
        color = theme.PROC_COLORS[cidx]
        ymax = self._common_ymax()
        for key, it in self.items.items():
            s = self.sums[key]
            it.update_data(series(self.results[key], self.metric), ymax, color, step,
                           f"T {fmt(s['t_prom'])} · E {fmt(s['e_prom'])}\n{s['cambios']} cambios de contexto")
            it.selected = key == self.algo
        top = f"{ymax:g} %" if self.metric == "cpu" else f"{ymax:g}"
        self.graph.set_data(series(self.results[self.algo], self.metric), ymax, color, step,
                            desc, top, vfmt, animate)
        self.big_title.setText(title)
        self.big_algo.setText(ALGORITMOS[self.algo])
        s = self.sums[self.algo]
        self.stat_values["utilizacion"].setText(f"{s['utilizacion']:.0f} %" if s["utilizacion"] == int(s["utilizacion"])
                                                else f"{fmt(s['utilizacion'], 1)} %")
        self.stat_values["cambios"].setText(str(s["cambios"]))
        self.stat_values["tiempo_cambios"].setText(str(s["tiempo_cambios"]))
        self.stat_values["cola_maxima"].setText(fmt(s["cola_maxima"]))
        self.stat_values["tiempo_total"].setText(str(s["tiempo_total"]))
        self.stat_values["t_prom"].setText(fmt(s["t_prom"]))
        self.stat_values["e_prom"].setText(fmt(s["e_prom"]))
        self.stat_values["i_prom"].setText(fmt(s["i_prom"]))
        self.stat_values["por_unidad"].setText(fmt(s["por_unidad"]))
        for it in self.items.values():
            it.update()

    def select_algo(self, key: str):
        self.algo = key
        if self.results:
            self._refresh_graphics(animate=True)

    def select_metric(self, key: str):
        self.metric = key
        if self.results:
            self._refresh_graphics(animate=True)
