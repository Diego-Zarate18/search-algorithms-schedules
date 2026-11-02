"""Reproducción paso a paso de una búsqueda ya resuelta.

``Reproductor`` aplica los eventos de un ``Resultado`` uno por uno y
mantiene lo que la interfaz necesita mostrar: el horario parcial, el
último paso, los contadores y una bitácora. No depende de Tkinter, por
lo que se prueba de forma automática.
"""

from __future__ import annotations

from collections import deque

from .busqueda import Evento, Resultado, TipoEvento
from .modelo import Sesion


class Reproductor:
    """Recorre la traza de eventos hacia adelante y hacia atrás.

    Retroceder un paso vuelve a aplicar la traza desde el inicio; con
    trazas de decenas de miles de eventos sigue siendo inmediato.
    """

    def __init__(self, resultado: Resultado, tam_bitacora: int = 200) -> None:
        self.resultado = resultado
        self.eventos = resultado.eventos
        self._tam_bitacora = tam_bitacora
        self.reiniciar()

    # Navegación -------------------------------------------------------

    def reiniciar(self) -> None:
        """Vuelve al estado inicial: horario vacío y ningún paso aplicado."""
        self.indice = 0
        self.asignaciones: dict[str, Sesion] = {}
        self.foco: Evento | None = None
        self.explorados = 0
        self.retrocesos = 0
        self.bitacora: deque[str] = deque(maxlen=self._tam_bitacora)

    def avanzar(self, pasos: int = 1) -> int:
        """Aplica hasta ``pasos`` eventos y devuelve cuántos aplicó."""
        aplicados = 0
        while aplicados < pasos and not self.terminado:
            self._aplicar(self.eventos[self.indice])
            self.indice += 1
            aplicados += 1
        return aplicados

    def retroceder(self, pasos: int = 1) -> None:
        """Deshace hasta ``pasos`` eventos."""
        self.ir_a(self.indice - pasos)

    def ir_a(self, indice: int) -> None:
        """Deja aplicados exactamente los primeros ``indice`` eventos."""
        indice = max(0, min(indice, self.total))
        if indice < self.indice:
            self.reiniciar()
        self.avanzar(indice - self.indice)

    def ir_al_final(self) -> None:
        self.ir_a(self.total)

    # Consultas --------------------------------------------------------

    @property
    def total(self) -> int:
        return len(self.eventos)

    @property
    def terminado(self) -> bool:
        return self.indice >= self.total

    @property
    def colocadas(self) -> int:
        return len(self.asignaciones)

    # Interno ----------------------------------------------------------

    def _aplicar(self, evento: Evento) -> None:
        etiqueta = evento.bloque.etiqueta if evento.bloque else None
        if evento.tipo is TipoEvento.PROBAR:
            self.explorados += 1
        elif evento.tipo is TipoEvento.ACEPTAR:
            self.asignaciones[etiqueta] = evento.sesion
        elif evento.tipo is TipoEvento.RETROCEDER:
            del self.asignaciones[etiqueta]
            self.retrocesos += 1
        self.foco = evento
        self.bitacora.append(f"{self.indice + 1:>6}  {describir(evento, breve=True)}")


def describir(evento: Evento, breve: bool = False) -> str:
    """Descripción legible de un evento.

    Con ``breve=True`` el motivo de rechazo se abrevia a 'R1'…'R4' (bitácora).
    """
    tipo = evento.tipo
    if tipo is TipoEvento.SOLUCION:
        return f"Solución encontrada: {evento.nivel} sesiones colocadas"
    if tipo is TipoEvento.SIN_SOLUCION:
        return "No existe solución: se agotaron todas las alternativas"

    lugar = f"{evento.sesion.id} en {evento.bloque.etiqueta}"
    if tipo is TipoEvento.PROBAR:
        return f"Probar {lugar}"
    if tipo is TipoEvento.ACEPTAR:
        return f"Aceptar {lugar}"
    if tipo is TipoEvento.RECHAZAR:
        motivo = evento.motivo.value[:2] if breve else evento.motivo.value
        return f"Rechazar {lugar} · {motivo}"
    return f"Retroceder: quitar {evento.sesion.id} de {evento.bloque.etiqueta}"
