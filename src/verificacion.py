"""Verificación final independiente de un horario (métricas 1–3).

No reutiliza ``restricciones.validar``: en lugar de evaluar candidato por
candidato, revisa el horario completo agrupando asignaciones por bloque,
por día y por materia. Así sirve como comprobación cruzada del agente.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

from .modelo import Asignacion, Escenario, EstadoHorario


class Regla(Enum):
    """Regla incumplida por un conflicto."""

    INTEGRIDAD = "La asignación no corresponde a los datos del escenario"
    R1 = "Dos sesiones del grupo en el mismo bloque"
    R2 = "Docente ocupado con otro grupo en ese bloque"
    R3 = "Más de una sesión de la materia el mismo día"
    R4 = "Sesiones equivalentes fuera de orden de días"


@dataclass(frozen=True)
class Conflicto:
    """Incumplimiento detectado y las sesiones involucradas."""

    regla: Regla
    sesiones: tuple[str, ...]
    detalle: str


@dataclass(frozen=True)
class Verificacion:
    """Resultado de verificar un horario.

    El horario es válido solo si está completo y no tiene conflictos.
    """

    sesiones_asignadas: int
    sesiones_faltantes: tuple[str, ...]
    materias_asignadas: int
    total_materias: int
    conflictos: tuple[Conflicto, ...]

    @property
    def completo(self) -> bool:
        return not self.sesiones_faltantes

    @property
    def valido(self) -> bool:
        return self.completo and not self.conflictos


def verificar(escenario: Escenario, estado: EstadoHorario) -> Verificacion:
    """Revisa el horario completo contra los datos y las reglas R1–R4."""
    asignaciones = list(estado.asignaciones.values())
    conflictos = _integridad(escenario, asignaciones)
    validas = [a for a in asignaciones if not _es_ajena(escenario, a)]

    conflictos += _grupo(validas)
    conflictos += _docentes(escenario, validas)
    conflictos += _distribucion(validas)
    conflictos += _orden(escenario, estado)

    asignadas = {a.sesion.id for a in validas}
    faltantes = tuple(s.id for s in escenario.sesiones if s.id not in asignadas)
    materias_completas = sum(
        all(s.id in asignadas for s in escenario.sesiones_de(m.id))
        for m in escenario.materias
    )
    return Verificacion(
        sesiones_asignadas=len(asignadas),
        sesiones_faltantes=faltantes,
        materias_asignadas=materias_completas,
        total_materias=len(escenario.materias),
        conflictos=tuple(conflictos),
    )


def _es_ajena(escenario: Escenario, asignacion: Asignacion) -> bool:
    return (
        asignacion.sesion not in escenario.sesiones
        or asignacion.bloque not in escenario.bloques
    )


def _integridad(
    escenario: Escenario, asignaciones: list[Asignacion]
) -> list[Conflicto]:
    return [
        Conflicto(
            Regla.INTEGRIDAD,
            (a.sesion.id,),
            f"{a.sesion.id} en {a.bloque.etiqueta} no pertenece al escenario",
        )
        for a in asignaciones
        if _es_ajena(escenario, a)
    ]


def _grupo(asignaciones: list[Asignacion]) -> list[Conflicto]:
    por_bloque: dict[str, list[str]] = defaultdict(list)
    for a in asignaciones:
        por_bloque[a.bloque.etiqueta].append(a.sesion.id)
    return [
        Conflicto(Regla.R1, tuple(ids), f"{len(ids)} sesiones en {bloque}")
        for bloque, ids in por_bloque.items()
        if len(ids) > 1
    ]


def _docentes(escenario: Escenario, asignaciones: list[Asignacion]) -> list[Conflicto]:
    return [
        Conflicto(
            Regla.R2,
            (a.sesion.id,),
            f"{a.sesion.docente} está ocupado en {a.bloque.etiqueta}",
        )
        for a in asignaciones
        if escenario.docente_ocupado(a.sesion.docente, a.bloque)
    ]


def _distribucion(asignaciones: list[Asignacion]) -> list[Conflicto]:
    por_materia_y_dia: dict[tuple[str, str], list[str]] = defaultdict(list)
    for a in asignaciones:
        por_materia_y_dia[(a.sesion.materia.id, a.bloque.dia)].append(a.sesion.id)
    return [
        Conflicto(
            Regla.R3, tuple(ids), f"{materia} tiene {len(ids)} sesiones el {dia}"
        )
        for (materia, dia), ids in por_materia_y_dia.items()
        if len(ids) > 1
    ]


def _orden(escenario: Escenario, estado: EstadoHorario) -> list[Conflicto]:
    conflictos = []
    for materia in escenario.materias:
        sesiones = escenario.sesiones_de(materia.id)
        # Pares consecutivos de igual duración (excluye la sesión de 1 h de Inglés).
        for previa, actual in zip(sesiones, sesiones[1:]):
            if previa.duracion_horas != actual.duracion_horas:
                continue
            a_previa = estado.asignacion_de(previa.id)
            a_actual = estado.asignacion_de(actual.id)
            if a_previa is None or a_actual is None:
                continue
            if a_actual.bloque.indice_dia <= a_previa.bloque.indice_dia:
                conflictos.append(
                    Conflicto(
                        Regla.R4,
                        (previa.id, actual.id),
                        f"{actual.id} ({a_actual.bloque.dia}) no va después de "
                        f"{previa.id} ({a_previa.bloque.dia})",
                    )
                )
    return conflictos
