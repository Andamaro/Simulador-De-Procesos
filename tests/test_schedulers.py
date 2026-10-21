import pytest

from app.core import Process, fmt, simulate
from app.data.examples import EJERCICIO_LIBRETA, EJERCICIO_PIZARRON


def col(r, attr):
    return [getattr(m, attr) for m in r.metrics]


def test_fcfs_libreta():
    r = simulate("FCFS", EJERCICIO_LIBRETA)
    assert col(r, "finish") == [8, 17, 22, 25, 29, 35]
    assert col(r, "service") == [8, 15, 19, 21, 23, 28]
    assert col(r, "wait") == [0, 6, 14, 18, 19, 22]
    assert fmt(r.avg_service) == "19"
    assert fmt(r.avg_wait) == "13.167"


def test_fcfs_pizarron():
    r = simulate("FCFS", EJERCICIO_PIZARRON)
    assert col(r, "finish") == [5, 8, 9, 11]
    assert col(r, "wait") == [0, 4, 6, 6]
    assert fmt(r.avg_service) == "6.75"
    assert fmt(r.avg_wait) == "4"


def test_sjf_pizarron():
    r = simulate("SJF", EJERCICIO_PIZARRON)
    assert [(s.name, s.start, s.end) for s in r.segments] == [
        ("A", 0, 5), ("C", 5, 6), ("D", 6, 8), ("B", 8, 11)]
    assert (r.avg_service, r.avg_wait) == (6.0, 3.25)


def test_srtf_pizarron():
    r = simulate("SRTF", EJERCICIO_PIZARRON)
    assert [(s.name, s.start, s.end) for s in r.segments] == [
        ("A", 0, 1), ("B", 1, 2), ("C", 2, 3), ("B", 3, 5), ("D", 5, 7), ("A", 7, 11)]
    assert (r.avg_service, r.avg_wait) == (5.0, 2.25)


def test_rr_pizarron_quantum_2():
    r = simulate("RR", EJERCICIO_PIZARRON, quantum=2)
    assert [(s.name, s.start, s.end) for s in r.segments] == [
        ("A", 0, 2), ("B", 2, 4), ("C", 4, 5), ("A", 5, 7),
        ("D", 7, 9), ("B", 9, 10), ("A", 10, 11)]
    assert (r.avg_service, r.avg_wait) == (7.25, 4.5)


def test_cpu_inactiva():
    r = simulate("FCFS", [Process("A", 0, 2), Process("B", 5, 1)])
    assert r.segments[1].idle and (r.segments[1].start, r.segments[1].end) == (2, 5)


def test_empate_por_orden_de_captura():
    r = simulate("FCFS", [Process("X", 0, 1), Process("Y", 0, 1)])
    assert [s.name for s in r.segments] == ["X", "Y"]


def test_conservacion_de_trabajo():
    for alg in ("FCFS", "SJF", "SRTF", "RR"):
        r = simulate(alg, EJERCICIO_LIBRETA, quantum=3)
        assert sum(s.length for s in r.segments if not s.idle) == 35
        assert all(m.wait >= 0 for m in r.metrics)


def test_validaciones():
    with pytest.raises(ValueError):
        simulate("FCFS", [])
    with pytest.raises(ValueError):
        simulate("FCFS", [Process("A", 0, 1), Process("a", 1, 1)])
    with pytest.raises(ValueError):
        simulate("RR", EJERCICIO_PIZARRON, quantum=0)
    with pytest.raises(ValueError):
        Process("A", 0, 0)


def test_fmt():
    assert fmt(13.16666) == "13.167"
    assert fmt(19.0) == "19"
    assert fmt(0.0005) == "0.001"


def test_cola_de_listos_en_el_tiempo():
    r = simulate("FCFS", EJERCICIO_PIZARRON)
    assert r.queue_at(2.5) == ("A", ["B", "C"])
    assert r.queue_at(11) == (None, [])
    rr = simulate("RR", EJERCICIO_PIZARRON, quantum=2)
    assert rr.queue_at(2) == ("B", ["C", "A"])


def test_series_y_resumen():
    from app.core.analytics import series, summary
    for alg in ("FCFS", "SJF", "SRTF", "RR"):
        r = simulate(alg, EJERCICIO_PIZARRON, quantum=2)
        assert series(r, "done")[-1] == 4
        assert series(r, "ready")[-1] == 0
        assert series(r, "wait")[-1] == sum(m.wait for m in r.metrics)
        assert series(r, "cpu")[-1] == 100.0
    assert summary(simulate("FCFS", EJERCICIO_PIZARRON))["cola_maxima"] == 3
    assert summary(simulate("FCFS", EJERCICIO_PIZARRON))["cambios"] == 3
    assert summary(simulate("RR", EJERCICIO_PIZARRON, 2))["cambios"] == 6
    assert summary(simulate("SRTF", EJERCICIO_PIZARRON))["cambios"] == 5


def test_uso_de_cpu_con_hueco():
    from app.core.analytics import summary
    r = simulate("FCFS", [Process("A", 0, 2), Process("B", 4, 2)])
    assert summary(r)["utilizacion"] == pytest.approx(4 / 6 * 100)


def test_costo_de_cambio_de_contexto_fcfs():
    from app.core.analytics import summary
    r = simulate("FCFS", EJERCICIO_PIZARRON, switch_cost=1)
    assert [(s.name, s.start, s.end, s.overhead) for s in r.segments] == [
        ("A", 0, 5, False), (None, 5, 6, True), ("B", 6, 9, False), (None, 9, 10, True),
        ("C", 10, 11, False), (None, 11, 12, True), ("D", 12, 14, False)]
    assert (r.avg_service, r.avg_wait) == (8.25, 5.5)
    s = summary(r)
    assert s["cambios"] == 3 and s["tiempo_cambios"] == 3
    assert s["utilizacion"] == pytest.approx(11 / 14 * 100)


def test_costo_cero_no_altera_nada():
    for alg in ("FCFS", "SJF", "SRTF", "RR"):
        assert simulate(alg, EJERCICIO_LIBRETA, 3, 0).segments == simulate(alg, EJERCICIO_LIBRETA, 3).segments


def test_costo_invariantes_todos_los_algoritmos():
    from app.core.analytics import series, summary
    for alg in ("FCFS", "SJF", "SRTF", "RR"):
        for cost in (1, 2):
            r = simulate(alg, EJERCICIO_LIBRETA, 3, cost)
            s = summary(r)
            assert sum(x.length for x in r.segments if x.name) == 35
            assert s["tiempo_cambios"] == s["cambios"] * cost
            assert series(r, "wait")[-1] == sum(m.wait for m in r.metrics)
            ends = [x.end for x in r.segments]
            assert all(a.end == b.start for a, b in zip(r.segments, r.segments[1:]))


def test_rr_con_costo_no_cobra_si_sigue_el_mismo():
    r = simulate("RR", [Process("A", 0, 6)], quantum=2, switch_cost=3)
    assert not any(s.overhead for s in r.segments)
