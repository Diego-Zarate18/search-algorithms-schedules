"""Restricciones del problema (R1–R4), evaluadas sobre cada candidato.

Este módulo es el único lugar donde viven las reglas del problema.
``validar`` no modifica el estado: solo decide si el candidato
(sesión, bloque) puede agregarse y, si no, por qué.
"""

from __future__ import annotations

from enum import Enum

from .modelo import Asignacion, BloqueHorario, Escenario, EstadoHorario, Sesion


class MotivoRechazo(Enum):
    """Motivo por el que un candidato (sesión, bloque) es rechazado."""

    BLOQUE_OCUPADO_POR_GRUPO = "R1: el grupo ya tiene una sesión en ese bloque"
    DOCENTE_OCUPADO = "R2: el docente está ocupado con otro grupo"
    MATERIA_YA_TIENE_SESION_ESE_DIA = "R3: la materia ya tiene una sesión ese día"
    VIOLA_ORDEN_DE_SESIONES = "R4: debe ir en un día posterior a su sesión anterior"


def validar(
    escenario: Escenario,
    estado: EstadoHorario,
    sesion: Sesion,
    bloque: BloqueHorario,
) -> MotivoRechazo | None:
    """Devuelve ``None`` si la asignación es válida o el primer motivo de rechazo.

    Las reglas se revisan siempre en el orden R1 → R2 → R3 → R4, de modo
    que el motivo reportado es determinista.
    """
    # R1: el grupo no puede tener dos sesiones en el mismo bloque.
    if estado.sesion_en(bloque) is not None:
        return MotivoRechazo.BLOQUE_OCUPADO_POR_GRUPO

    # R2: el docente no puede estar dando clase a otro grupo en ese bloque.
    if escenario.docente_ocupado(sesion.docente, bloque):
        return MotivoRechazo.DOCENTE_OCUPADO

    asignadas = estado.por_materia(sesion.materia.id)

    # R3: como máximo una sesión de la materia por día.
    if any(a.bloque.indice_dia == bloque.indice_dia for a in asignadas):
        return MotivoRechazo.MATERIA_YA_TIENE_SESION_ESE_DIA

    # R4: sesiones equivalentes en días estrictamente crecientes.
    anterior = _anterior_equivalente(sesion, asignadas)
    if anterior is not None and bloque.indice_dia <= anterior.bloque.indice_dia:
        return MotivoRechazo.VIOLA_ORDEN_DE_SESIONES

    return None


def _anterior_equivalente(
    sesion: Sesion, asignadas: tuple[Asignacion, ...]
) -> Asignacion | None:
    """Asignación de la sesión anterior de la misma materia, si es equivalente.

    Dos sesiones son equivalentes si duran lo mismo (por eso la sesión de
    1 h de Inglés queda exenta). Si la anterior aún no está asignada, no
    hay contra qué comparar y R4 no aplica.
    """
    if sesion.numero == 1:
        return None
    duracion_anterior = sesion.materia.duraciones[sesion.numero - 2]
    if duracion_anterior != sesion.duracion_horas:
        return None
    return next((a for a in asignadas if a.sesion.numero == sesion.numero - 1), None)
