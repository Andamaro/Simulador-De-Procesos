import html

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QTextBrowser,
                               QVBoxLayout, QWidget)

from app.data.glossary import BIBLIOGRAFIA, TEMAS
from app.ui import theme
from app.ui.widgets.glass import GlassPanel

CSS = f"""
body {{ color: {theme.BONE}; font-family: '{theme.BODY}', 'Segoe UI'; font-size: 10.5pt; line-height: 150%; }}
h2 {{ font-family: '{theme.DISPLAY}', 'Segoe UI'; font-size: 20pt; margin: 0 0 6px 0; }}
h3 {{ font-family: '{theme.DISPLAY}', 'Segoe UI'; font-size: 12pt; margin: 20px 0 6px 0; }}
p.sum {{ color: #CFCFCF; margin: 0 0 4px 0; }}
td.term {{ color: {theme.BONE}; font-weight: bold; padding: 6px 18px 6px 0; vertical-align: top; width: 28%; }}
td.def {{ color: #CFCFCF; padding: 6px 0; vertical-align: top; border-bottom: 1px solid #262626; }}
.muted {{ color: {theme.MIST}; }}
"""


CORTOS = {"2.5": "Niveles, objetivos y criterios", "2.6": "Técnicas del planificador"}


def _esc(s: str) -> str:
    return html.escape(s)


class GlossaryView(QWidget):
    def __init__(self, open_view=None, parent=None):
        super().__init__(parent)
        self.open_view = open_view
        self.current = 0
        self._build()
        self.show_topic(0)

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.viewport().setAutoFillBackground(False)
        outer.addWidget(scroll)
        inner = QWidget()
        inner.setMinimumSize(900, 600)
        scroll.setWidget(inner)
        root = QVBoxLayout(inner)
        root.setContentsMargins(0, 0, 4, 0)
        root.setSpacing(14)

        head = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(2)
        h1 = QLabel("Glosario")
        h1.setObjectName("h1")
        sub = QLabel("Unidad 2 · Administración de procesos y del procesador")
        sub.setObjectName("muted")
        titles.addWidget(h1)
        titles.addWidget(sub)
        head.addLayout(titles)
        head.addStretch()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar un término")
        self.search.setClearButtonEnabled(True)
        self.search.setFixedWidth(260)
        self.search.setStyleSheet("QLineEdit { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.14);"
                                  " border-radius: 6px; padding: 6px 10px; }")
        self.search.textChanged.connect(self._on_search)
        head.addWidget(self.search, 0, Qt.AlignBottom)
        root.addLayout(head)

        sheet = GlassPanel()
        sh = QHBoxLayout(sheet)
        sh.setContentsMargins(0, 0, 0, 0)
        sh.setSpacing(0)
        root.addWidget(sheet, 1)

        side = QWidget()
        side.setFixedWidth(300)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(0, 12, 0, 12)
        sl.setSpacing(0)
        self.buttons: list[QPushButton] = []
        for i, t in enumerate(TEMAS):
            b = QPushButton(f"{t['id']}  {CORTOS.get(t['id'], t['title'])}")
            b.setObjectName("rail")
            b.setCheckable(True)
            b.setToolTip(t["title"])
            b.clicked.connect(lambda _=False, i=i: self.show_topic(i))
            sl.addWidget(b)
            self.buttons.append(b)
        bib = QPushButton("Bibliografía")
        bib.setObjectName("rail")
        bib.setCheckable(True)
        bib.clicked.connect(lambda: self.show_topic(len(TEMAS)))
        sl.addWidget(bib)
        self.buttons.append(bib)
        sl.addStretch()
        sh.addWidget(side)
        line = QFrame()
        line.setObjectName("hair")
        line.setFixedWidth(1)
        sh.addWidget(line)

        self.browser = QTextBrowser()
        self.browser.setOpenLinks(False)
        self.browser.document().setDefaultStyleSheet(CSS)
        self.browser.setStyleSheet("QTextBrowser { background: transparent; border: none; padding: 14px 26px; }")
        self.browser.anchorClicked.connect(self._on_link)
        sh.addWidget(self.browser, 1)

    def _topic_html(self, t: dict) -> str:
        out = [f"<h2>{_esc(t['id'])}  {_esc(t['title'])}</h2><p class='sum'>{_esc(t['summary'])}</p>"]
        for title, items in t["secciones"]:
            out.append(f"<h3>{_esc(title)}</h3><table width='100%' cellspacing='0'>")
            for term, d in items:
                out.append(f"<tr><td class='term' width='27%'>{_esc(term)}</td><td class='def'>{_esc(d)}</td></tr>")
            out.append("</table>")
        if t["id"] == "2.2":
            out.append("<p><a href='view:2' style='color:#ECECEC'>Ver el recorrido paso a paso en Estados</a></p>")
        if t["id"] in ("2.5", "2.6"):
            out.append("<p><a href='view:1' style='color:#ECECEC'>Comparar los algoritmos en Rendimiento</a></p>")
        return "".join(out)

    def show_topic(self, i: int):
        self.search.blockSignals(True)
        self.search.clear()
        self.search.blockSignals(False)
        self.current = i
        for j, b in enumerate(self.buttons):
            b.setChecked(j == i)
        if i < len(TEMAS):
            self.browser.setHtml(self._topic_html(TEMAS[i]))
        else:
            items = "".join(f"<tr><td class='def'>{_esc(b)}</td></tr>" for b in BIBLIOGRAFIA)
            self.browser.setHtml("<h2>Bibliografía</h2><p class='sum'>Referencias mínimas para ampliar los temas de la unidad. "
                                 "Confirma edición y año con el ejemplar que consultes.</p>"
                                 f"<table width='100%' cellspacing='0'>{items}</table>")
        self.browser.verticalScrollBar().setValue(0)

    def _on_search(self, text: str):
        q = text.strip().lower()
        if not q:
            self.show_topic(self.current)
            return
        for b in self.buttons:
            b.setChecked(False)
        out = [f"<h2>Resultados</h2><p class='muted'>Búsqueda: «{_esc(text.strip())}»</p>"]
        n = 0
        for t in TEMAS:
            rows = [(s, term, d) for s, items in t["secciones"] for term, d in items
                    if q in term.lower() or q in d.lower()]
            if not rows:
                continue
            out.append(f"<h3>{_esc(t['id'])}  {_esc(t['title'])}</h3><table width='100%' cellspacing='0'>")
            for _s, term, d in rows:
                out.append(f"<tr><td class='term' width='27%'>{_esc(term)}</td><td class='def'>{_esc(d)}</td></tr>")
                n += 1
            out.append("</table>")
        if n == 0:
            out.append("<p>No hay términos que coincidan. Prueba con una palabra más corta, por ejemplo «hilo» o «quantum».</p>")
        self.browser.setHtml("".join(out))

    def _on_link(self, url):
        s = url.toString()
        if s.startswith("view:") and self.open_view:
            self.open_view(int(s.split(":")[1]))
