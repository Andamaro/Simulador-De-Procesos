"""Ejercicios hechos en clase (FCFS)."""
from app.core import Process

EJERCICIO_LIBRETA = [
    Process("A", 0, 8), Process("B", 2, 9), Process("C", 3, 5),
    Process("D", 4, 3), Process("E", 6, 4), Process("F", 7, 6),
]
EJERCICIO_PIZARRON = [
    Process("A", 0, 5), Process("B", 1, 3), Process("C", 2, 1), Process("D", 3, 2),
]
EJEMPLOS = {
    "Ejercicio de libreta (6 procesos)": EJERCICIO_LIBRETA,
    "Ejercicio del pizarrón (4 procesos)": EJERCICIO_PIZARRON,
}
