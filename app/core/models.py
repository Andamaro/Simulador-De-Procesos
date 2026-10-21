"""Modelos y métricas. Nomenclatura de clase: T = tiempo de servicio
(retorno), E = tiempo de espera, I = índice de servicio (T_exe / T)."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

MAX_PROCESOS = 12


@dataclass(frozen=True)
class Process:
    name: str
    arrival: int   # I_LL: instante de llegada
    burst: int     # T_exe: tiempo de ejecución

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("El proceso necesita un nombre.")
        if self.arrival < 0:
            raise ValueError(f"{self.name}: la llegada no puede ser negativa.")
        if self.burst < 1:
            raise ValueError(f"{self.name}: la ejecución debe ser al menos 1.")


@dataclass(frozen=True)
class Segment:
    """Tramo de la gráfica. name=None significa CPU inactiva."""
    name: str | None
    start: int
    end: int
    ready: tuple[str, ...] = ()   # cola de listos al iniciar el tramo

    @property
    def idle(self) -> bool:
        return self.name is None

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass(frozen=True)
class ProcessMetrics:
    name: str
    arrival: int
    burst: int
    finish: int        # I_final
    service: int       # T = I_final - I_LL
    wait: int          # E = T - T_exe
    index: float       # I = T_exe / T


@dataclass(frozen=True)
class Step:
    time: int
    text: str


@dataclass
class Result:
    algorithm: str
    segments: list[Segment]
    metrics: list[ProcessMetrics]
    steps: list[Step]

    @property
    def avg_service(self) -> float:
        return sum(m.service for m in self.metrics) / len(self.metrics)

    @property
    def avg_wait(self) -> float:
        return sum(m.wait for m in self.metrics) / len(self.metrics)

    @property
    def avg_index(self) -> float:
        return sum(m.index for m in self.metrics) / len(self.metrics)

    @property
    def makespan(self) -> int:
        return self.segments[-1].end if self.segments else 0


def fmt(value: float, places: int = 3) -> str:
    """Redondea (mitad hacia arriba) a máximo `places` decimales, sin ceros sobrantes."""
    q = Decimal(1).scaleb(-places)
    s = format(Decimal(str(value)).quantize(q, ROUND_HALF_UP), "f")
    return s.rstrip("0").rstrip(".") if "." in s else s
