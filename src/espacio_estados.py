"""Tamaño del espacio de estados, calculado por niveles de restricción.

Reproduce las cifras del reporte (sección "Espacio de estados"):

1. Sin restricciones: cada sesión en cualquier bloque, ``B ** S``.
2. Con R1 (bloques distintos): permutaciones ``P(B, S)``.
3. Con R1, R3 y R4, sin ocupaciones de docentes.
4. Con todas las restricciones (R1–R4): horarios válidos del escenario.

Los niveles 3 y 4 se cuentan exactamente con programación dinámica día
por día. Por R3 cada materia aparece a lo más una vez por día, y por R4
las sesiones equivalentes quedan determinadas por el conjunto de días
que ocupan; así basta decidir, para cada día, qué materias tienen sesión
y de cuántas formas caben en bloques distintos.

Uso: ``python -m src.espacio_estados``
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from functools import lru_cache

from .modelo import Escenario


@dataclass(frozen=True)
class EspacioDeEstados:
    """Horarios completos posibles en cada nivel de restricción."""

    sin_restricciones: int
    con_r1: int
    con_r1_r3_r4: int
    validos: int
    nodos_con_r1: int


def sin_restricciones(escenario: Escenario) -> int:
    return len(escenario.bloques) ** len(escenario.sesiones)


def con_r1(escenario: Escenario) -> int:
    return math.perm(len(escenario.bloques), len(escenario.sesiones))


def nodos_con_r1(escenario: Escenario) -> int:
    """Cota de estados parciales (nodos del árbol) con R1: suma de P(B, k)."""
    b, s = len(escenario.bloques), len(escenario.sesiones)
    return sum(math.perm(b, k) for k in range(s + 1))


def horarios_validos(escenario: Escenario, con_ocupaciones: bool = True) -> int:
    """Cuenta los horarios completos que cumplen R1, R3, R4 y, opcionalmente, R2."""
    dias = list(dict.fromkeys(b.dia for b in escenario.bloques))
    bloques_por_dia = {d: [b for b in escenario.bloques if b.dia == d] for d in dias}

    # Tramos: sesiones consecutivas de igual duración (R4 las ordena por día).
    tramos: list[tuple[int, int]] = []  # (índice de materia, número de sesiones)
    for i, materia in enumerate(escenario.materias):
        for _, grupo in itertools.groupby(materia.duraciones):
            tramos.append((i, len(list(grupo))))
    tramos_de = {
        i: [t for t, (m, _) in enumerate(tramos) if m == i]
        for i in range(len(escenario.materias))
    }

    libres = {
        (d, i): [
            b.id
            for b in bloques_por_dia[d]
            if not (con_ocupaciones and escenario.docente_ocupado(m.docente, b))
        ]
        for d in dias
        for i, m in enumerate(escenario.materias)
    }

    @lru_cache(maxsize=None)
    def formas_del_dia(dia: str, materias: tuple[int, ...]) -> int:
        """Formas de dar a las materias elegidas bloques distintos y libres."""

        def colocar(k: int, usados: frozenset[str]) -> int:
            if k == len(materias):
                return 1
            return sum(
                colocar(k + 1, usados | {b})
                for b in libres[(dia, materias[k])]
                if b not in usados
            )

        return colocar(0, frozenset())

    @lru_cache(maxsize=None)
    def contar(indice_dia: int, restante: tuple[int, ...]) -> int:
        if indice_dia == len(dias):
            return int(not any(restante))
        dias_restantes = len(dias) - indice_dia
        # Poda: una materia no puede necesitar más días de los que quedan (R3).
        if any(
            sum(restante[t] for t in ts) > dias_restantes for ts in tramos_de.values()
        ):
            return 0

        dia = dias[indice_dia]
        opciones = [
            [None] + [t for t in ts if restante[t] > 0] for ts in tramos_de.values()
        ]
        total = 0
        for eleccion in itertools.product(*opciones):
            materias = tuple(i for i, t in enumerate(eleccion) if t is not None)
            if len(materias) > len(bloques_por_dia[dia]):
                continue
            formas = formas_del_dia(dia, materias)
            if formas == 0:
                continue
            nuevo = list(restante)
            for t in eleccion:
                if t is not None:
                    nuevo[t] -= 1
            total += formas * contar(indice_dia + 1, tuple(nuevo))
        return total

    return contar(0, tuple(n for _, n in tramos))


def calcular(escenario: Escenario) -> EspacioDeEstados:
    return EspacioDeEstados(
        sin_restricciones=sin_restricciones(escenario),
        con_r1=con_r1(escenario),
        con_r1_r3_r4=horarios_validos(escenario, con_ocupaciones=False),
        validos=horarios_validos(escenario),
        nodos_con_r1=nodos_con_r1(escenario),
    )


def main() -> None:
    from .escenarios import ESCENARIOS

    primero = next(iter(ESCENARIOS.values()))()
    base = calcular(primero)
    b, s = len(primero.bloques), len(primero.sesiones)
    print(f"Niveles comunes a todos los casos ({s} sesiones, {b} bloques):")
    filas = (
        (f"1. Sin restricciones ({b}^{s})", base.sin_restricciones),
        (f"2. Con R1 (P({b},{s}))", base.con_r1),
        ("3. Con R1, R3 y R4 (sin docentes)", base.con_r1_r3_r4),
        ("   Cota de nodos del árbol con R1", base.nodos_con_r1),
    )
    for texto, valor in filas:
        print(f"  {texto:<36}{valor:>32,}")
    print("\nNivel 4. Horarios válidos con todas las restricciones (R1–R4):")
    for crear in ESCENARIOS.values():
        escenario = crear()
        print(f"  {escenario.nombre:<36}{horarios_validos(escenario):>32,}")


if __name__ == "__main__":
    main()
