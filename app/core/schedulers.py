"""FCFS, SJF (sin expropiación), SRTF (con expropiación) y Round Robin.

Desempates: por llegada y luego por orden de captura. Si la CPU queda sin
trabajo se registra un tramo inactivo. En Round Robin, los procesos que llegan
en el mismo instante en que expira un quantum entran a la cola antes que el
proceso expropiado.
"""
from __future__ import annotations

from collections import deque
from typing import Callable, Sequence

from .models import MAX_PROCESOS, Process, ProcessMetrics, Result, Segment, Step

QUANTUM_DEFECTO = 2


def _validate(procs: Sequence[Process]) -> None:
    if not procs:
        raise ValueError("Agrega al menos un proceso.")
    if len(procs) > MAX_PROCESOS:
        raise ValueError(f"El máximo es {MAX_PROCESOS} procesos.")
    names = [p.name.strip().lower() for p in procs]
    if len(set(names)) != len(names):
        raise ValueError("Los nombres de proceso deben ser únicos.")


def _nonpreemptive(procs: Sequence[Process], key: Callable) -> list[Segment]:
    pending = list(enumerate(procs))
    t, segs = 0, []
    while pending:
        avail = sorted((x for x in pending if x[1].arrival <= t), key=key)
        if not avail:
            nxt = min(p.arrival for _, p in pending)
            segs.append(Segment(None, t, nxt))
            t = nxt
            continue
        i, p = avail[0]
        segs.append(Segment(p.name, t, t + p.burst, tuple(q.name for _, q in avail[1:])))
        t += p.burst
        pending.remove((i, p))
    return segs


def _fcfs(procs):
    return _nonpreemptive(procs, key=lambda x: (x[1].arrival, x[0]))


def _sjf(procs):
    return _nonpreemptive(procs, key=lambda x: (x[1].burst, x[1].arrival, x[0]))


def _srtf(procs):
    rem = {i: p.burst for i, p in enumerate(procs)}
    t, segs = 0, []
    while rem:
        order = lambda i: (rem[i], procs[i].arrival, i)
        avail = sorted((i for i in rem if procs[i].arrival <= t), key=order)
        if not avail:
            nxt = min(procs[i].arrival for i in rem)
            segs.append(Segment(None, t, nxt))
            t = nxt
            continue
        i = avail[0]
        end = t + rem[i]
        future = [procs[j].arrival for j in rem if procs[j].arrival > t]
        if future:
            end = min(end, min(future))
        last = segs[-1] if segs else None
        if last and last.name == procs[i].name and last.end == t:
            segs[-1] = Segment(last.name, last.start, end, last.ready)
        else:
            segs.append(Segment(procs[i].name, t, end, tuple(procs[j].name for j in avail[1:])))
        rem[i] -= end - t
        t = end
        if rem[i] == 0:
            del rem[i]
    return segs


def _rr(procs, quantum: int):
    if quantum < 1:
        raise ValueError("El quantum debe ser al menos 1.")
    n = len(procs)
    order = sorted(range(n), key=lambda i: (procs[i].arrival, i))
    rem = {i: p.burst for i, p in enumerate(procs)}
    queue: deque[int] = deque()
    k, t, segs = 0, 0, []

    def admit(upto: int):
        nonlocal k
        while k < n and procs[order[k]].arrival <= upto:
            queue.append(order[k])
            k += 1

    while k < n or queue:
        admit(t)
        if not queue:
            nxt = procs[order[k]].arrival
            segs.append(Segment(None, t, nxt))
            t = nxt
            continue
        i = queue.popleft()
        run = min(quantum, rem[i])
        segs.append(Segment(procs[i].name, t, t + run, tuple(procs[j].name for j in queue)))
        t += run
        rem[i] -= run
        admit(t)
        if rem[i] > 0:
            queue.append(i)
    return segs


def _metrics(procs: Sequence[Process], segs: list[Segment]) -> list[ProcessMetrics]:
    finish = {s.name: s.end for s in segs if not s.idle}
    out = []
    for p in procs:
        f = finish[p.name]
        t = f - p.arrival
        out.append(ProcessMetrics(p.name, p.arrival, p.burst, f, t, t - p.burst, p.burst / t))
    return out


def _narrate(algorithm: str, segs: list[Segment], metrics: list[ProcessMetrics]) -> list[Step]:
    by_name = {m.name: m for m in metrics}
    steps = []
    for s in segs:
        if s.idle:
            steps.append(Step(s.start, f"La CPU queda inactiva hasta t={s.end}: no hay procesos listos."))
            continue
        cola = ", ".join(s.ready) if s.ready else "vacía"
        steps.append(Step(s.start, f"{s.name} pasa a Ejecutando. Cola de listos: {cola}."))
        m = by_name[s.name]
        if s.end == m.finish:
            steps.append(Step(s.end, f"{s.name} termina. T = {m.finish} − {m.arrival} = {m.service}; "
                                     f"E = {m.service} − {m.burst} = {m.wait}."))
        elif algorithm == "RR":
            steps.append(Step(s.end, f"A {s.name} se le acaba el quantum y regresa al final de la cola."))
        else:
            steps.append(Step(s.end, f"{s.name} es expropiado: llegó un proceso con menos tiempo restante."))
    return steps


ALGORITMOS = {
    "FCFS": "FCFS (primero en llegar, primero en servirse)",
    "SJF": "SJF (el más corto primero, sin expropiación)",
    "SRTF": "SRTF (menor tiempo restante, con expropiación)",
    "RR": "Round Robin (turnos con quantum)",
}


def simulate(algorithm: str, procs: Sequence[Process], quantum: int = QUANTUM_DEFECTO) -> Result:
    _validate(procs)
    if algorithm == "FCFS":
        segs = _fcfs(procs)
    elif algorithm == "SJF":
        segs = _sjf(procs)
    elif algorithm == "SRTF":
        segs = _srtf(procs)
    elif algorithm == "RR":
        segs = _rr(procs, quantum)
    else:
        raise ValueError(f"Algoritmo desconocido: {algorithm}")
    metrics = _metrics(procs, segs)
    return Result(algorithm, segs, metrics, _narrate(algorithm, segs, metrics))
