"""Entidades del problema de generación de horarios."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Iterable


@dataclass(frozen=True)
class Materia:
    """Materia que debe programarse para un grupo."""

    id: str
    nombre: str
    docente: str
    horas_semana: int


@dataclass(frozen=True)
class Sesion:
    """Sesión de una materia que ocupará un bloque horario."""

    id: str
    materia: Materia
    numero: int
    duracion_horas: int


@dataclass(frozen=True)
class BloqueHorario:
    """Bloque de dos horas disponible dentro de la jornada."""

    dia: str
    id: str
    hora_inicio: str
    hora_fin: str

    @property
    def clave(self) -> tuple[str, str]:
        """Devuelve la clave estable usada para identificar el bloque."""
        return self.dia, self.id


@dataclass(frozen=True)
class Asignacion:
    """Ubicación de una sesión dentro del horario del grupo."""

    sesion: Sesion
    bloque: BloqueHorario
    aula: str


@dataclass
class EstadoHorario:
    """Estado parcial o completo del horario generado."""

    asignaciones: dict[str, Asignacion] = field(default_factory=dict)

    def agregar(self, asignacion: Asignacion) -> None:
        """Agrega una asignación y rechaza sesiones o bloques duplicados."""
        if asignacion.sesion.id in self.asignaciones:
            raise ValueError(f"La sesión ya está asignada: {asignacion.sesion.id}")

        if any(
            existente.bloque.clave == asignacion.bloque.clave
            for existente in self.asignaciones.values()
        ):
            raise ValueError(
                f"El bloque ya está ocupado: {asignacion.bloque.dia}-"
                f"{asignacion.bloque.id}"
            )

        self.asignaciones[asignacion.sesion.id] = asignacion

    def remover(self, sesion: Sesion) -> Asignacion:
        """Remueve y devuelve la asignación de una sesión."""
        try:
            return self.asignaciones.pop(sesion.id)
        except KeyError as error:
            raise KeyError(f"La sesión no está asignada: {sesion.id}") from error

    def contiene(self, sesion: Sesion) -> bool:
        """Indica si la sesión ya forma parte del estado."""
        return sesion.id in self.asignaciones

    def bloque_ocupado(self, bloque: BloqueHorario) -> bool:
        """Indica si el grupo ya usa el bloque indicado."""
        return any(
            asignacion.bloque.clave == bloque.clave
            for asignacion in self.asignaciones.values()
        )

    def por_materia(self, materia_id: str) -> tuple[Asignacion, ...]:
        """Devuelve las asignaciones actuales de una materia."""
        return tuple(
            asignacion
            for asignacion in self.asignaciones.values()
            if asignacion.sesion.materia.id == materia_id
        )

    def copiar(self) -> "EstadoHorario":
        """Devuelve una copia independiente del estado actual."""
        return EstadoHorario(asignaciones=dict(self.asignaciones))

    @property
    def cantidad(self) -> int:
        """Devuelve el número de sesiones asignadas."""
        return len(self.asignaciones)


@dataclass
class Metricas:
    """Contadores que utilizará posteriormente el algoritmo de búsqueda."""

    estados_explorados: int = 0
    retrocesos: int = 0
    retrocesos_por_nivel: dict[int, int] = field(default_factory=dict)
    tiempo_segundos: float = 0.0

    def iniciar_cronometro(self) -> float:
        """Devuelve una marca de tiempo para iniciar una medición."""
        return perf_counter()

    def finalizar_cronometro(self, inicio: float) -> None:
        """Acumula el tiempo transcurrido desde una marca de tiempo."""
        self.tiempo_segundos = perf_counter() - inicio

    def registrar_retroceso(self, nivel: int) -> None:
        """Registra un retroceso total y lo asocia con un nivel del árbol."""
        self.retrocesos += 1
        self.retrocesos_por_nivel[nivel] = (
            self.retrocesos_por_nivel.get(nivel, 0) + 1
        )


@dataclass(frozen=True)
class Escenario:
    """Datos inmutables de un escenario de programación."""

    nombre: str
    grupo: str
    aula: str
    materias: tuple[Materia, ...]
    sesiones: tuple[Sesion, ...]
    bloques: tuple[BloqueHorario, ...]
    ocupaciones_docentes: frozenset[tuple[str, str, str]]

    def ocupacion_docente(
        self, docente: str, bloque: BloqueHorario
    ) -> bool:
        """Indica si un docente está ocupado en el bloque indicado."""
        return (docente, bloque.dia, bloque.id) in self.ocupaciones_docentes

    def sesiones_de(self, materia_id: str) -> tuple[Sesion, ...]:
        """Devuelve las sesiones de una materia en su orden de creación."""
        return tuple(
            sesion for sesion in self.sesiones if sesion.materia.id == materia_id
        )

    def validar_integridad(self) -> None:
        """Comprueba las invariantes básicas de los datos del escenario."""
        if len(self.materias) != 7:
            raise ValueError("El escenario debe contener exactamente 7 materias.")

        if len(self.sesiones) != 18:
            raise ValueError("El escenario debe contener exactamente 18 sesiones.")

        if len(self.bloques) != 20:
            raise ValueError("El escenario debe contener exactamente 20 bloques.")

        horas_por_materia = {
            materia.id: sum(
                sesion.duracion_horas
                for sesion in self.sesiones
                if sesion.materia.id == materia.id
            )
            for materia in self.materias
        }
        for materia in self.materias:
            if horas_por_materia[materia.id] != materia.horas_semana:
                raise ValueError(
                    f"La carga de {materia.id} no coincide con sus sesiones."
                )

        ids_sesiones = [sesion.id for sesion in self.sesiones]
        if len(ids_sesiones) != len(set(ids_sesiones)):
            raise ValueError("Las sesiones deben tener identificadores únicos.")

        ids_bloques = [bloque.clave for bloque in self.bloques]
        if len(ids_bloques) != len(set(ids_bloques)):
            raise ValueError("Los bloques deben tener identificadores únicos.")


def total_horas(sesiones: Iterable[Sesion]) -> int:
    """Devuelve la suma de horas de las sesiones recibidas."""
    return sum(sesion.duracion_horas for sesion in sesiones)
