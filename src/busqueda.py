"""Agente DFS con retroceso (búsqueda no informada).

``AgenteDFS(escenario).resolver()`` recorre las sesiones y los bloques en
el orden fijo del escenario, sin heurísticas. Además de las métricas,
registra cada paso como un ``Evento`` para que la interfaz pueda
reproducir la búsqueda después (nunca se ejecuta dentro de Tkinter).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .metricas import Metricas
from .modelo import Asignacion, BloqueHorario, Escenario, EstadoHorario, Sesion
from .restricciones import MotivoRechazo, validar


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


@dataclass(frozen=True)
class Resultado:
    """Salida de una búsqueda completa."""

    encontrado: bool
    estado: EstadoHorario
    metricas: Metricas
    eventos: tuple[Evento, ...]


class AgenteDFS:
    """Búsqueda en profundidad con retroceso sobre un escenario.

    Con ``registrar_eventos=False`` no se guarda la traza; útil para medir
    el tiempo de la búsqueda sin el costo de registrar cada paso.
    """

    def __init__(self, escenario: Escenario, registrar_eventos: bool = True) -> None:
        self.escenario = escenario
        self.registrar_eventos = registrar_eventos
        self._estado = EstadoHorario()
        self._metricas = Metricas()
        self._eventos: list[Evento] = []

    def resolver(self) -> Resultado:
        """Ejecuta la búsqueda desde el estado inicial (horario vacío)."""
        self._estado = EstadoHorario()
        self._metricas = Metricas()
        self._eventos = []

        self._metricas.iniciar_cronometro()
        encontrado = self._dfs(0)
        self._metricas.detener_cronometro()

        if not encontrado:
            self._emitir(TipoEvento.SIN_SOLUCION, 0)

        return Resultado(
            encontrado=encontrado,
            estado=self._estado,
            metricas=self._metricas,
            eventos=tuple(self._eventos),
        )

    def _dfs(self, nivel: int) -> bool:
        sesiones = self.escenario.sesiones
        if nivel == len(sesiones):
            self._emitir(TipoEvento.SOLUCION, nivel)
            return True

        sesion = sesiones[nivel]
        for bloque in self.escenario.bloques:
            self._metricas.registrar_exploracion()
            self._emitir(TipoEvento.PROBAR, nivel, sesion, bloque)

            motivo = validar(self.escenario, self._estado, sesion, bloque)
            if motivo is not None:
                self._emitir(TipoEvento.RECHAZAR, nivel, sesion, bloque, motivo)
                continue

            self._estado.agregar(Asignacion(sesion, bloque))
            self._emitir(TipoEvento.ACEPTAR, nivel, sesion, bloque)

            if self._dfs(nivel + 1):
                return True

            # La rama no llevó a solución: se deshace y se prueba el siguiente bloque.
            self._estado.remover(sesion)
            self._metricas.registrar_retroceso(nivel)
            self._emitir(TipoEvento.RETROCEDER, nivel, sesion, bloque)

        return False

    def _emitir(
        self,
        tipo: TipoEvento,
        nivel: int,
        sesion: Sesion | None = None,
        bloque: BloqueHorario | None = None,
        motivo: MotivoRechazo | None = None,
    ) -> None:
        if self.registrar_eventos:
            self._eventos.append(Evento(tipo, nivel, sesion, bloque, motivo))
