from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from app.ui.widgets.glass import GlassPanel


class CreditsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 4, 0)
        root.setSpacing(14)
        h1 = QLabel("Créditos")
        h1.setObjectName("h1")
        root.addWidget(h1)
        sheet = GlassPanel()
        lay = QVBoxLayout(sheet)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(4)

        def line(text, name="", gap=0):
            lbl = QLabel(text)
            if name:
                lbl.setObjectName(name)
            lay.addSpacing(gap)
            lay.addWidget(lbl)

        line("Simulador de planificación de procesos", "h2")
        line("Sistemas Operativos · Unidad 2: Administración de procesos y del procesador", "muted")
        line("Equipo", "muted", 18)
        line("Andrés Cruz Guzmán")
        line("Jorge Antonet López Figueroa")
        line("Grupo y carrera", "muted", 18)
        line("Grupo 3 O · Ingeniería en Sistemas Computacionales")
        line("Institución", "muted", 18)
        line("Tecnológico Nacional de México · Instituto Tecnológico del Istmo")
        line("Tipografías", "muted", 18)
        line("Bricolage Grotesque e IBM Plex Sans, bajo licencia SIL Open Font License.")
        lay.addStretch()
        root.addWidget(sheet, 1)
