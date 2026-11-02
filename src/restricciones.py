"""Restricciones del problema (R1–R4), evaluadas sobre cada candidato.

Contrato (pendiente de implementar):

    validar(escenario, estado, sesion, bloque) -> MotivoRechazo | None

Devuelve ``None`` si la asignación es válida, o el motivo del primer
rechazo detectado. El motivo se muestra en la interfaz y en el reporte.
Este módulo es el único lugar donde viven las reglas del problema.
"""

from __future__ import annotations

from enum import Enum


class MotivoRechazo(Enum):
    """Motivo por el que un candidato (sesión, bloque) es rechazado."""

    BLOQUE_OCUPADO_POR_GRUPO = "R1: el grupo ya tiene una sesión en ese bloque"
    DOCENTE_OCUPADO = "R2: el docente está ocupado con otro grupo"
    MATERIA_YA_TIENE_SESION_ESE_DIA = "R3: la materia ya tiene una sesión ese día"
    VIOLA_ORDEN_DE_SESIONES = "R4: debe ir en un día posterior a su sesión anterior"
