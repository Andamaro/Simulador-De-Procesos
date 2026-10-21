"""Series por unidad de tiempo y resumen para la vista Rendimiento."""
from __future__ import annotations

from .models import Result

SERIES = ("cpu", "ready", "done", "wait")


def _executed(result: Result, name: str, t: float) -> float:
    return sum(min(s.end, t) - s.start for s in result.segments if s.name == name and s.start < t)


def _busy(result: Result, t: float) -> float:
    return sum(min(s.end, t) - s.start for s in result.segments if s.name is not None and s.start < t)


def series(result: Result, kind: str) -> list[float]:
    """Valor en cada instante entero 0..makespan.

    cpu   uso de CPU acumulado (%)
    ready procesos en la cola de listos
    done  procesos terminados
    wait  espera acumulada de todos los procesos (suma de lo que han esperado hasta t)
    """
    m = result.makespan
    out: list[float] = []
    for t in range(m + 1):
        if kind == "cpu":
            if t == 0:
                seg = result.segment_at(0)
                out.append(100.0 if seg and not seg.idle else 0.0)
            else:
                out.append(_busy(result, t) / t * 100)
        elif kind == "ready":
            out.append(float(len(result.queue_at(t)[1])))
        elif kind == "done":
            out.append(float(sum(1 for x in result.metrics if x.finish <= t)))
        elif kind == "wait":
            total = 0.0
            for x in result.metrics:
                elapsed = max(0, min(t, x.finish) - x.arrival)
                total += elapsed - _executed(result, x.name, t)
            out.append(total)
        else:
            raise ValueError(kind)
    return out


def summary(result: Result) -> dict:
    m = result.makespan
    cpu_segs = [s for s in result.segments if s.name is not None]
    switches = sum(1 for a, b in zip(cpu_segs, cpu_segs[1:]) if a.name != b.name)
    return {
        "utilizacion": _busy(result, m) / m * 100,
        "cola_maxima": max(series(result, "ready")),
        "cambios": switches,
        "tiempo_cambios": sum(x.length for x in result.segments if x.overhead),
        "por_unidad": len(result.metrics) / m,
        "tiempo_total": m,
        "t_prom": result.avg_service,
        "e_prom": result.avg_wait,
        "i_prom": result.avg_index,
    }
