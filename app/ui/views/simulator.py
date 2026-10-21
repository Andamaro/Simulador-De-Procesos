import random

from PySide6.QtCore import QElapsedTimer, Qt, QTimer
from PySide6.QtGui import QColor, QFontMetrics
from PySide6.QtWidgets import (QAbstractItemView, QAbstractSpinBox, QFrame, QGridLayout, QScrollArea, QButtonGroup, QComboBox, QHBoxLayout, QHeaderView,
                               QLabel, QListWidget, QListWidgetItem, QPushButton, QSlider, QSpinBox,
                               QStyledItemDelegate, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from app.core import ALGORITMOS, COSTO_MAX, MAX_PROCESOS, QUANTUM_DEFECTO, Process, fmt, simulate
from app.data.examples import EJEMPLOS
from app.ui import theme
from app.ui.widgets.chips import ChipRow
from app.ui.widgets.gantt import GanttWidget
from app.ui.widgets.glass import GlassPanel

TICKS_POR_SEGUNDO = 1.5
VELOCIDADES = [("0.5×", 0.5), ("1×", 1.0), ("2×", 2.0), ("4×", 4.0)]
EPS = 1e-9


class _SpinDelegate(QStyledItemDelegate):
    def __init__(self, lo: int, hi: int, parent=None):
        super().__init__(parent)
        self.lo, self.hi = lo, hi

    def createEditor(self, parent, option, index):
        sb = QSpinBox(parent)
        sb.setRange(self.lo, self.hi)
        sb.setFrame(False)
        sb.setButtonSymbols(QAbstractSpinBox.NoButtons)
        return sb

    def setEditorData(self, editor, index):
        editor.setValue(int(index.data() or self.lo))

    def setModelData(self, editor, model, index):
        editor.interpretText()
        model.setData(index, str(editor.value()))


def _hair(vertical: bool = False) -> QFrame:
    f = QFrame()
    f.setObjectName("hair")
    f.setFixedWidth(1) if vertical else f.setFixedHeight(1)
    return f


def _section(title: str | None = None):
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(20, 16, 20, 16)
    lay.setSpacing(10)
    head = None
    if title:
        head = QHBoxLayout()
        lbl = QLabel(title)
        lbl.setObjectName("h2")
        head.addWidget(lbl)
        head.addStretch()
        lay.addLayout(head)
    return w, lay, head


def _fit(btn: QPushButton, factor: float = 1.0) -> QPushButton:
    """Evita recortes de texto: el ancho mínimo sale del texto real."""
    btn.setMinimumWidth(int(QFontMetrics(btn.font()).horizontalAdvance(btn.text()) * factor) + 30)
    return btn


class SimulatorView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.algorithm = "FCFS"
        self.result = None
        self.colors: dict[str, QColor] = {}
        self.t = 0.0
        self.speed = 1.0
        self._loading = False
        self._shown_steps = -1
        self.clock = QElapsedTimer()
        self._last_ms = 0
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._tick)
        self._build()
        self.load_processes(EJEMPLOS["Ejercicio del pizarrón (4 procesos)"], autoplay=False)

    # ------------------------------------------------------------------ UI
    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.viewport().setAutoFillBackground(False)
        outer.addWidget(scroll)
        inner = QWidget()
        inner.setMinimumSize(980, 660)          # por debajo de esto aparece desplazamiento, no encimado
        scroll.setWidget(inner)
        root = QVBoxLayout(inner)
        root.setContentsMargins(0, 0, 4, 0)
        root.setSpacing(14)

        # encabezado: título y algoritmo
        row = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(2)
        h1 = QLabel("Planificación de procesos")
        h1.setObjectName("h1")
        self.subtitle = QLabel(ALGORITMOS["FCFS"])
        self.subtitle.setObjectName("muted")
        titles.addWidget(h1)
        titles.addWidget(self.subtitle)
        row.addLayout(titles)
        row.addStretch()
        self.group = QButtonGroup(self)
        for key, text in (("FCFS", "FCFS"), ("SJF", "SJF"), ("SRTF", "SRTF"), ("RR", "Round Robin")):
            b = QPushButton(text)
            b.setObjectName("tab")
            b.setCheckable(True)
            b.setProperty("alg", key)
            b.setChecked(key == "FCFS")
            _fit(b)
            self.group.addButton(b)
            row.addWidget(b)
        self.group.buttonClicked.connect(self._on_algorithm)
        root.addLayout(row)

        # una sola hoja de cristal; la estructura la dan las líneas finas
        sheet = GlassPanel()
        sh = QHBoxLayout(sheet)
        sh.setContentsMargins(0, 0, 0, 0)
        sh.setSpacing(0)
        root.addWidget(sheet, 1)

        left, ll, lh = _section("Procesos")
        left.setFixedWidth(340)
        self.count = QLabel("")
        self.count.setObjectName("muted")
        lh.addWidget(self.count)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Proceso", "Llegada", "Ejecución"])
        for i, tip in enumerate(["Nombre del proceso", "I_LL: instante de llegada",
                                 "T_exe: tiempo de ejecución"]):
            self.table.horizontalHeaderItem(i).setToolTip(tip)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setItemDelegateForColumn(1, _SpinDelegate(0, 999, self.table))
        self.table.setItemDelegateForColumn(2, _SpinDelegate(1, 999, self.table))
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.itemChanged.connect(lambda _: self.recompute())
        ll.addWidget(self.table, 1)
        self.error = QLabel("")
        self.error.setObjectName("error")
        self.error.setWordWrap(True)
        ll.addWidget(self.error)
        ll.addWidget(_hair())
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        self.q_label = QLabel("Quantum")
        self.q_label.setToolTip("Tiempo máximo de cada turno en Round Robin")
        self.quantum = QSpinBox()
        self.quantum.setRange(1, 20)
        self.quantum.setValue(QUANTUM_DEFECTO)
        self.quantum.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.q_minus, self.q_plus = QPushButton("−"), QPushButton("+")
        self.q_value = QLabel(str(QUANTUM_DEFECTO))
        self.c_label = QLabel("Cambio de contexto")
        self.c_label.setToolTip("Tiempo que la CPU pierde al pasar de un proceso a otro. 0 = sin costo (como en clase)")
        self.switch_cost = QSpinBox()
        self.switch_cost.setRange(0, COSTO_MAX)
        self.switch_cost.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.c_minus, self.c_plus = QPushButton("−"), QPushButton("+")
        self.c_value = QLabel("0")
        for r, (lab, spin, mn, val, pl) in enumerate((
                (self.q_label, self.quantum, self.q_minus, self.q_value, self.q_plus),
                (self.c_label, self.switch_cost, self.c_minus, self.c_value, self.c_plus))):
            val.setObjectName("h2")
            val.setAlignment(Qt.AlignCenter)
            val.setFixedWidth(30)
            for b2, d in ((mn, -1), (pl, 1)):
                b2.setObjectName("step")
                b2.clicked.connect(lambda _=False, sp=spin, d=d: sp.setValue(sp.value() + d))
            spin.valueChanged.connect(lambda v, lb=val: lb.setText(str(v)))
            spin.valueChanged.connect(lambda _: self.recompute())
            grid.addWidget(lab, r, 0)
            grid.addWidget(mn, r, 1)
            grid.addWidget(val, r, 2)
            grid.addWidget(pl, r, 3)
        grid.setColumnStretch(0, 1)
        ll.addLayout(grid)
        self._set_quantum_enabled(False)
        btns = QHBoxLayout()
        for text, fn in (("Agregar", self.add_process), ("Quitar", self.remove_process),
                         ("Aleatorio", self.randomize)):
            b = _fit(QPushButton(text))
            b.clicked.connect(fn)
            btns.addWidget(b)
        ll.addLayout(btns)
        self.examples = QComboBox()
        self.examples.addItem("Cargar ejemplo de clase")
        self.examples.addItems(list(EJEMPLOS))
        self.examples.activated.connect(self._on_example)
        ll.addWidget(self.examples)
        sh.addWidget(left)
        sh.addWidget(_hair(True))

        rightw = QWidget()
        right = QVBoxLayout(rightw)
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        sh.addWidget(rightw, 1)

        gsec, gl, gh = _section("Gráfica de Gantt")
        self.time_label = QLabel("t = 0")
        self.time_label.setObjectName("h2")
        gh.addWidget(self.time_label)
        self.gantt = GanttWidget()
        gl.addWidget(self.gantt, 1)
        strip = QHBoxLayout()
        strip.setSpacing(28)
        for attr, title, size in (("run_chip", "Ejecutando", 40), ("ready_chips", "Cola de listos", 32)):
            col = QVBoxLayout()
            col.setSpacing(4)
            lab = QLabel(title)
            lab.setObjectName("muted")
            lab.setFixedHeight(20)
            chips = ChipRow(size)
            setattr(self, attr, chips)
            col.addWidget(lab)
            col.addWidget(chips)
            strip.addLayout(col, 0 if attr == "run_chip" else 1)
            strip.setAlignment(col, Qt.AlignTop)
        self.run_chip.setMinimumWidth(160)
        gl.addLayout(strip)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.sliderPressed.connect(self.pause)
        self.slider.sliderMoved.connect(lambda v: self.set_time(v / 100))
        gl.addWidget(self.slider)
        ctl = QHBoxLayout()
        self.btn_reset = _fit(QPushButton("Reiniciar"))
        self.btn_prev = _fit(QPushButton("Anterior"))
        self.btn_play = _fit(QPushButton("Reproducir"), 1.1)
        self.btn_play.setObjectName("primary")
        self.btn_next = _fit(QPushButton("Siguiente"))
        self.btn_end = _fit(QPushButton("Ver completo"))
        self.btn_reset.clicked.connect(lambda: (self.pause(), self.set_time(0)))
        self.btn_prev.clicked.connect(lambda: self.jump(-1))
        self.btn_next.clicked.connect(lambda: self.jump(+1))
        self.btn_end.clicked.connect(lambda: (self.pause(), self.set_time(self.total())))
        self.btn_play.clicked.connect(self.toggle_play)
        for b in (self.btn_reset, self.btn_prev, self.btn_play, self.btn_next, self.btn_end):
            ctl.addWidget(b)
        ctl.addStretch()
        sp = QLabel("Velocidad")
        sp.setObjectName("muted")
        ctl.addWidget(sp)
        self.speed_box = QComboBox()
        for text, _ in VELOCIDADES:
            self.speed_box.addItem(text)
        self.speed_box.setCurrentIndex(1)
        self.speed_box.currentIndexChanged.connect(lambda i: setattr(self, "speed", VELOCIDADES[i][1]))
        ctl.addWidget(self.speed_box)
        gl.addLayout(ctl)
        right.addWidget(gsec, 3)
        right.addWidget(_hair())

        lower = QHBoxLayout()
        lower.setSpacing(0)
        lw = QWidget()
        lw.setLayout(lower)
        right.addWidget(lw, 2)

        ssec, sl, sheadl = _section("Paso a paso")
        self.step_count = QLabel("")
        self.step_count.setObjectName("muted")
        sheadl.addWidget(self.step_count)
        self.steps = QListWidget()
        self.steps.setWordWrap(True)
        self.steps.setTextElideMode(Qt.ElideNone)
        self.steps.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.steps.setSelectionMode(QAbstractItemView.NoSelection)
        sl.addWidget(self.steps, 1)
        lower.addWidget(ssec, 2)
        lower.addWidget(_hair(True))

        rsec, rl, _h = _section("Resultados")
        self.results = QTableWidget(0, 5)
        self.results.setHorizontalHeaderLabels(["Proceso", "I final", "T", "E", "I"])
        for i, tip in enumerate(["", "Instante de finalización", "T, tiempo de servicio = I_final − I_LL",
                                 "E, tiempo de espera = T − T_exe", "I, índice de servicio = T_exe ÷ T"]):
            self.results.horizontalHeaderItem(i).setToolTip(tip)
        self.results.verticalHeader().setVisible(False)
        self.results.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.results.verticalHeader().setDefaultSectionSize(30)
        self.results.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.results.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results.setSelectionMode(QAbstractItemView.NoSelection)
        rl.addWidget(self.results, 1)
        legend = QLabel("T servicio · E espera · I índice de servicio")
        legend.setObjectName("muted")
        rl.addWidget(legend)
        self.formulas = QLabel("")
        self.formulas.setObjectName("muted")
        self.formulas.setWordWrap(True)
        rl.addWidget(self.formulas)
        lower.addWidget(rsec, 3)

    def current_inputs(self):
        """(procesos, quantum, costo de cambio de contexto, error) para otras vistas."""
        procs, err = self._read_table()
        q, c = self.quantum.value(), self.switch_cost.value()
        if err:
            return None, q, c, "Corrige la tabla de procesos en el Simulador: " + err
        if not procs:
            return None, q, c, "Agrega al menos un proceso en el Simulador."
        return procs, q, c, ""

    def _set_quantum_enabled(self, on: bool) -> None:
        for w in (self.q_label, self.q_minus, self.q_value, self.q_plus):
            w.setEnabled(on)

    # ------------------------------------------------------------ procesos
    def _next_name(self) -> str:
        used = {self.table.item(r, 0).text().strip().upper() for r in range(self.table.rowCount())
                if self.table.item(r, 0)}
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if c not in used:
                return c
        return f"P{self.table.rowCount() + 1}"

    def _append_row(self, name: str, arrival: int, burst: int) -> None:
        r = self.table.rowCount()
        self.table.insertRow(r)
        for c, text in enumerate((name, str(arrival), str(burst))):
            self.table.setItem(r, c, QTableWidgetItem(text))

    def load_processes(self, procs, autoplay: bool) -> None:
        self._loading = True
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for p in procs:
            self._append_row(p.name, p.arrival, p.burst)
        self.table.blockSignals(False)
        self._loading = False
        self.recompute(show_all=not autoplay)
        if autoplay:
            self.play()

    def add_process(self):
        if self.table.rowCount() >= MAX_PROCESOS:
            self.error.setText(f"El máximo es {MAX_PROCESOS} procesos.")
            return
        self.table.blockSignals(True)
        self._append_row(self._next_name(), 0, 1)
        self.table.blockSignals(False)
        self.recompute()

    def remove_process(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        if not rows and self.table.rowCount():
            rows = [self.table.rowCount() - 1]
        self.table.blockSignals(True)
        for r in rows:
            self.table.removeRow(r)
        self.table.blockSignals(False)
        self.recompute()

    def randomize(self):
        n = random.randint(4, 7)
        procs = [Process("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[i], 0 if i == 0 else random.randint(0, 10),
                         random.randint(1, 9)) for i in range(n)]
        self.load_processes(procs, autoplay=True)

    def _on_example(self, idx: int):
        if idx > 0:
            self.group.buttons()[0].setChecked(True)
            self._set_algorithm("FCFS")
            self.load_processes(list(EJEMPLOS.values())[idx - 1], autoplay=True)
        self.examples.setCurrentIndex(0)

    def _read_table(self):
        procs = []
        for r in range(self.table.rowCount()):
            try:
                name = self.table.item(r, 0).text().strip()
                procs.append(Process(name, int(self.table.item(r, 1).text()), int(self.table.item(r, 2).text())))
            except (ValueError, AttributeError) as e:
                return None, f"Fila {r + 1}: {e}" if str(e) else f"Fila {r + 1}: revisa los valores."
        return procs, ""

    # ------------------------------------------------------------ algoritmo
    def _on_algorithm(self, button):
        self._set_algorithm(button.property("alg"))
        self.recompute()

    def _set_algorithm(self, key: str):
        self.algorithm = key
        self.subtitle.setText(ALGORITMOS[key])
        self._set_quantum_enabled(key == "RR")

    def recompute(self, show_all: bool = True):
        if self._loading:
            return
        self.pause()
        procs, err = self._read_table()
        self.count.setText(f"{self.table.rowCount()} de {MAX_PROCESOS}")
        if not err:
            try:
                self.result = simulate(self.algorithm, procs, self.quantum.value(), self.switch_cost.value())
            except ValueError as e:
                err = str(e)
        self.error.setText(err)
        if err:
            self.result = None
            self.colors = {}
        else:
            self.colors = {p.name: theme.PROC_COLORS[i % len(theme.PROC_COLORS)] for i, p in enumerate(procs)}
        self.gantt.set_result(self.result, self.colors)
        self.slider.setRange(0, int(self.total() * 100))
        self._shown_steps = -1
        self._fill_results_rows()
        self.set_time(self.total() if show_all else 0)

    # ------------------------------------------------------------ reproducción
    def total(self) -> int:
        return self.result.makespan if self.result else 0

    def play(self):
        if not self.result:
            return
        if self.t >= self.total() - EPS:
            self.set_time(0)
        self.clock.start()
        self._last_ms = 0
        self.timer.start()
        self.btn_play.setText("Pausar")

    def pause(self):
        self.timer.stop()
        self.btn_play.setText("Reproducir")

    def toggle_play(self):
        self.pause() if self.timer.isActive() else self.play()

    def _tick(self):
        now = self.clock.elapsed()
        dt = (now - self._last_ms) / 1000
        self._last_ms = now
        self.set_time(self.t + dt * TICKS_POR_SEGUNDO * self.speed)
        if self.t >= self.total() - EPS:
            self.pause()

    def jump(self, direction: int):
        if not self.result:
            return
        self.pause()
        marks = sorted({0, *[s.start for s in self.result.segments], *[s.end for s in self.result.segments]})
        if direction > 0:
            nxt = [m for m in marks if m > self.t + EPS]
            self.set_time(nxt[0] if nxt else self.total())
        else:
            prv = [m for m in marks if m < self.t - EPS]
            self.set_time(prv[-1] if prv else 0)

    # ------------------------------------------------------------ actualización
    def set_time(self, t: float):
        t = max(0.0, min(float(t), float(self.total())))
        self.t = t
        self.gantt.set_time(t)
        self.slider.blockSignals(True)
        self.slider.setValue(int(t * 100))
        self.slider.blockSignals(False)
        self.time_label.setText(f"t = {int(t) if t < self.total() else self.total()}")
        self._update_queue()
        self._update_results()
        self._update_steps()

    def _update_queue(self):
        if not self.result:
            self.run_chip.set_items([], "—")
            self.ready_chips.set_items([], "—")
            return
        running, queue = self.result.queue_at(self.t)
        done = self.t >= self.total() - EPS
        seg = self.result.segment_at(self.t)
        empty = "Terminó" if done else ("Cambio de contexto" if seg and seg.overhead else "CPU inactiva")
        self.run_chip.set_items([(running, self.colors[running])] if running else [], empty)
        self.ready_chips.set_items([(n, self.colors[n]) for n in queue], "Vacía")

    def _fill_results_rows(self):
        n = len(self.result.metrics) if self.result else 0
        self.results.setRowCount(n + 1 if n else 0)
        if not n:
            return
        for r, m in enumerate(self.result.metrics):
            name = QTableWidgetItem(m.name)
            name.setForeground(self.colors[m.name])
            self.results.setItem(r, 0, name)
            for c in range(1, 5):
                self.results.setItem(r, c, QTableWidgetItem(""))
        self.results.setItem(n, 0, QTableWidgetItem("Promedio"))
        for c in range(1, 5):
            self.results.setItem(n, c, QTableWidgetItem(""))

    def _update_results(self):
        if not self.result:
            self.formulas.setText("")
            return
        res, n = self.result, len(self.result.metrics)
        muted = QColor(theme.MIST)
        for r, m in enumerate(res.metrics):
            vals = [str(m.finish), str(m.service), str(m.wait), fmt(m.index)] if m.finish <= self.t + EPS else ["…"] * 4
            for c, v in enumerate(vals, start=1):
                it = self.results.item(r, c)
                it.setText(v)
                it.setForeground(QColor(theme.BONE) if v != "…" else muted)
        done = self.t >= self.total() - EPS
        avg = ["", fmt(res.avg_service), fmt(res.avg_wait), fmt(res.avg_index)] if done else ["", "…", "…", "…"]
        for c, v in enumerate(avg, start=1):
            it = self.results.item(n, c)
            it.setText(v)
            it.setForeground(QColor(theme.BONE) if done else muted)
        if done:
            st = sum(m.service for m in res.metrics)
            sw = sum(m.wait for m in res.metrics)
            self.formulas.setText(f"Servicio promedio = ΣT ÷ n = {st} ÷ {n} = {fmt(res.avg_service)}\n"
                                  f"Espera promedio = ΣE ÷ n = {sw} ÷ {n} = {fmt(res.avg_wait)}")
        else:
            self.formulas.setText("Los promedios aparecen cuando termina la simulación.")

    def _update_steps(self):
        if not self.result:
            self.steps.clear()
            self.step_count.setText("")
            self._shown_steps = -1
            return
        visible = [s for s in self.result.steps if s.time <= self.t + EPS]
        if len(visible) == self._shown_steps:
            return
        self._shown_steps = len(visible)
        self.steps.clear()
        for s in visible:
            self.steps.addItem(QListWidgetItem(f"t = {s.time}   {s.text}"))
        self.step_count.setText(f"{len(visible)} de {len(self.result.steps)}")
        self.steps.scrollToBottom()
