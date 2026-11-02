"""Contadores de rendimiento de la búsqueda (métricas 4, 5 y 6).

Las métricas 1 a 3 (validez, materias asignadas y conflictos finales)
se obtienen de la verificación final independiente (``verificacion.py``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter


@dataclass
class Metricas:
    """Estados explorados, retrocesos (total y por nivel) y tiempo."""

    estados_explorados: int = 0
    retrocesos: int = 0
    retrocesos_por_nivel: dict[int, int] = field(default_factory=dict)
    tiempo_segundos: float = 0.0
    _inicio: float | None = field(default=None, repr=False)

    def registrar_exploracion(self) -> None:
        """Cuenta un candidato (sesión, bloque) evaluado, válido o no."""
        self.estados_explorados += 1

    def registrar_retroceso(self, nivel: int) -> None:
        """Cuenta una asignación deshecha en el nivel ``nivel`` del árbol."""
        self.retrocesos += 1
        self.retrocesos_por_nivel[nivel] = self.retrocesos_por_nivel.get(nivel, 0) + 1

    def iniciar_cronometro(self) -> None:
        """Marca el inicio de la búsqueda."""
        self._inicio = perf_counter()

    def detener_cronometro(self) -> None:
        """Registra el tiempo transcurrido desde ``iniciar_cronometro``."""
        if self._inicio is None:
            raise RuntimeError("El cronómetro no se inició.")
        self.tiempo_segundos = perf_counter() - self._inicio
        self._inicio = None
