"""Agente DFS con retroceso (búsqueda no informada).

Contrato (pendiente de implementar): ``AgenteDFS(escenario).resolver()``
recorre las sesiones y los bloques en orden fijo, registra métricas y
emite una lista de ``Evento`` que la interfaz reproduce paso a paso
(la búsqueda nunca se ejecuta dentro del ciclo de eventos de Tkinter).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .modelo import BloqueHorario, Sesion
from .restricciones import MotivoRechazo


class TipoEvento(Enum):
    """Pasos observables de la búsqueda."""

    PROBAR = "probar"
    ACEPTAR = "aceptar"
    RECHAZAR = "rechazar"
    RETROCEDER = "retroceder"
    SOLUCION = "solucion"
    SIN_SOLUCION = "sin_solucion"


@dataclass(frozen=True)
class Evento:
    """Un paso de la búsqueda; ``nivel`` es el índice de la sesión (0–17)."""

    tipo: TipoEvento
    nivel: int
    sesion: Sesion | None = None
    bloque: BloqueHorario | None = None
    motivo: MotivoRechazo | None = None
