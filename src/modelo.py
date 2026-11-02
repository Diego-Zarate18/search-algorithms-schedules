"""Entidades del problema de generación de horarios.

Este módulo solo describe y almacena datos. Las reglas del problema
(R1–R4) viven exclusivamente en ``restricciones.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class Materia:
    """Materia que debe programarse para el grupo.

    ``duraciones`` indica la duración en horas de cada sesión, en orden.
    Por ejemplo, ``(2, 2, 2)`` son tres sesiones de dos horas.
    """

    id: str
    nombre: str
    docente: str
    duraciones: tuple[int, ...]

    @property
    def horas_semana(self) -> int:
        """Carga semanal de la materia, derivada de sus sesiones."""
        return sum(self.duraciones)


@dataclass(frozen=True)
class Sesion:
    """Sesión de una materia que ocupará un bloque horario completo."""

    id: str
    materia: Materia
    numero: int
    duracion_horas: int

    @property
    def docente(self) -> str:
        """Docente que imparte la sesión."""
        return self.materia.docente


@dataclass(frozen=True)
class BloqueHorario:
    """Bloque de dos horas dentro de la jornada.

    ``indice_dia`` permite comparar días (Lu=0 … Vi=4), necesario para la
    restricción de orden de sesiones.
    """

    dia: str
    indice_dia: int
    id: str
    hora_inicio: str
    hora_fin: str

    @property
    def clave(self) -> tuple[str, str]:
        """Clave estable del bloque, por ejemplo ``("Lu", "B1")``."""
        return self.dia, self.id

    @property
    def etiqueta(self) -> str:
        """Etiqueta legible del bloque, por ejemplo ``"Lu-B1"``."""
        return f"{self.dia}-{self.id}"


@dataclass(frozen=True)
class Asignacion:
    """Elemento del estado: una sesión ubicada en un bloque.

    El aula no forma parte de la asignación: el grupo tiene su propia
    aula y el problema consiste únicamente en ordenar el horario.
    """

    sesion: Sesion
    bloque: BloqueHorario


@dataclass
class EstadoHorario:
    """Estado parcial o completo del horario: S = {(sesión, bloque)}.

    No valida reglas del problema; solo almacena asignaciones y ofrece
    consultas rápidas para el validador y la interfaz.
    """

    asignaciones: dict[str, Asignacion] = field(default_factory=dict)

    def agregar(self, asignacion: Asignacion) -> None:
        """Agrega una asignación. Una sesión no puede asignarse dos veces."""
        if asignacion.sesion.id in self.asignaciones:
            raise ValueError(f"La sesión ya está asignada: {asignacion.sesion.id}")
        self.asignaciones[asignacion.sesion.id] = asignacion

    def remover(self, sesion: Sesion) -> Asignacion:
        """Remueve y devuelve la asignación de una sesión (retroceso)."""
        try:
            return self.asignaciones.pop(sesion.id)
        except KeyError as error:
            raise KeyError(f"La sesión no está asignada: {sesion.id}") from error

    def contiene(self, sesion: Sesion) -> bool:
        """Indica si la sesión ya forma parte del estado."""
        return sesion.id in self.asignaciones

    def asignacion_de(self, sesion_id: str) -> Asignacion | None:
        """Devuelve la asignación de una sesión, o ``None`` si no existe."""
        return self.asignaciones.get(sesion_id)

    def sesion_en(self, bloque: BloqueHorario) -> Asignacion | None:
        """Devuelve la asignación que ocupa el bloque, o ``None``."""
        for asignacion in self.asignaciones.values():
            if asignacion.bloque.clave == bloque.clave:
                return asignacion
        return None

    def por_materia(self, materia_id: str) -> tuple[Asignacion, ...]:
        """Asignaciones actuales de una materia."""
        return tuple(
            asignacion
            for asignacion in self.asignaciones.values()
            if asignacion.sesion.materia.id == materia_id
        )

    @property
    def cantidad(self) -> int:
        """Número de sesiones asignadas."""
        return len(self.asignaciones)


@dataclass(frozen=True)
class Escenario:
    """Datos inmutables de un caso de programación.

    ``grupo`` y ``aula`` son datos descriptivos (se muestran en la
    interfaz); no intervienen en la búsqueda.
    ``ocupaciones_docentes`` contiene tuplas ``(docente, dia, bloque_id)``.
    """

    nombre: str
    descripcion: str
    grupo: str
    aula: str
    materias: tuple[Materia, ...]
    sesiones: tuple[Sesion, ...]
    bloques: tuple[BloqueHorario, ...]
    ocupaciones_docentes: frozenset[tuple[str, str, str]]

    def docente_ocupado(self, docente: str, bloque: BloqueHorario) -> bool:
        """Indica si el docente está ocupado con otro grupo en el bloque."""
        return (docente, bloque.dia, bloque.id) in self.ocupaciones_docentes

    def sesiones_de(self, materia_id: str) -> tuple[Sesion, ...]:
        """Sesiones de una materia en su orden de creación."""
        return tuple(s for s in self.sesiones if s.materia.id == materia_id)

    @property
    def docentes(self) -> tuple[str, ...]:
        """Docentes de las materias del escenario, sin repetir."""
        return tuple(dict.fromkeys(m.docente for m in self.materias))

    def validar_integridad(self) -> None:
        """Comprueba la consistencia de los datos (no su tamaño).

        Acepta escenarios de cualquier tamaño (incluidos los escenarios
        mini para trazas manuales). Los conteos del caso base (7, 18, 20)
        se comprueban en las pruebas.
        """
        if not self.materias or not self.sesiones or not self.bloques:
            raise ValueError("El escenario necesita materias, sesiones y bloques.")

        _sin_duplicados((m.id for m in self.materias), "materias")
        _sin_duplicados((s.id for s in self.sesiones), "sesiones")
        _sin_duplicados((b.clave for b in self.bloques), "bloques")

        for materia in self.materias:
            if not materia.duraciones or any(d <= 0 for d in materia.duraciones):
                raise ValueError(f"Duraciones inválidas en {materia.id}.")
            if any(d > 2 for d in materia.duraciones):
                raise ValueError(
                    f"Una sesión de {materia.id} excede el bloque de 2 horas."
                )

        if self.sesiones != generar_sesiones(self.materias):
            raise ValueError(
                "Las sesiones no coinciden con las duraciones de las materias "
                "o no siguen el orden fijo de búsqueda."
            )

        indices_por_dia: dict[str, int] = {}
        for bloque in self.bloques:
            previo = indices_por_dia.setdefault(bloque.dia, bloque.indice_dia)
            if previo != bloque.indice_dia:
                raise ValueError(f"El día {bloque.dia} tiene índices distintos.")
        if len(set(indices_por_dia.values())) != len(indices_por_dia):
            raise ValueError("Dos días comparten el mismo índice.")

        claves_bloques = {b.clave for b in self.bloques}
        docentes = set(self.docentes)
        for docente, dia, bloque_id in self.ocupaciones_docentes:
            if docente not in docentes:
                raise ValueError(f"Ocupación de un docente inexistente: {docente}.")
            if (dia, bloque_id) not in claves_bloques:
                raise ValueError(
                    f"Ocupación en un bloque inexistente: {dia}-{bloque_id}."
                )


def generar_sesiones(materias: Iterable[Materia]) -> tuple[Sesion, ...]:
    """Genera las sesiones en el orden fijo de búsqueda (materia por materia)."""
    return tuple(
        Sesion(
            id=f"{materia.id}.{numero}",
            materia=materia,
            numero=numero,
            duracion_horas=duracion,
        )
        for materia in materias
        for numero, duracion in enumerate(materia.duraciones, start=1)
    )


def total_horas(sesiones: Iterable[Sesion]) -> int:
    """Suma de horas de las sesiones recibidas."""
    return sum(sesion.duracion_horas for sesion in sesiones)


def _sin_duplicados(valores: Iterable[object], que: str) -> None:
    lista = list(valores)
    if len(lista) != len(set(lista)):
        raise ValueError(f"Hay identificadores repetidos en {que}.")
