"""Escenarios (casos) del proyecto.

El caso 1 (base) está calibrado: con el orden fijo de búsqueda debe
producir 1 834 estados explorados y 83 retrocesos. Los casos 2 a 4 se
calibrarán una vez implementada la búsqueda (ver docs/decisiones_tecnicas.md).
"""

from __future__ import annotations

from typing import Callable, Mapping, Sequence

from .modelo import BloqueHorario, Escenario, Materia, generar_sesiones

GRUPO_OBJETIVO = "7° A"
AULA_DEL_GRUPO = "Aula 7A"

DIAS: tuple[str, ...] = ("Lu", "Ma", "Mi", "Ju", "Vi")

DEFINICION_BLOQUES: tuple[tuple[str, str, str], ...] = (
    ("B1", "08:00", "10:00"),
    ("B2", "10:00", "12:00"),
    ("B3", "12:00", "14:00"),
    ("B4", "14:00", "16:00"),
)


def crear_materias() -> tuple[Materia, ...]:
    """Las siete materias de 7° A, en el orden fijo de búsqueda."""
    return (
        Materia("M1", "Fundamentos de Inteligencia Artificial", "D1", (2, 2, 2)),
        Materia("M2", "Bases de Datos en la Nube (Optativa I)", "D2", (2, 2, 2)),
        Materia("M3", "Seguridad Informática", "D3", (2, 2, 2)),
        Materia("M4", "Inglés VI", "D4", (2, 2, 1)),
        Materia("M5", "Habilidades Gerenciales", "D5", (2, 2)),
        Materia("M6", "Formulación de Proyectos de Tecnología", "D6", (2, 2)),
        Materia(
            "M7",
            "Ética y Legislación en Tecnologías de la Información",
            "D7",
            (2, 2),
        ),
    )


def crear_bloques(
    dias: Sequence[str] = DIAS,
    definicion: Sequence[tuple[str, str, str]] = DEFINICION_BLOQUES,
) -> tuple[BloqueHorario, ...]:
    """Bloques en el orden fijo de búsqueda: día por día, B1 → B4."""
    return tuple(
        BloqueHorario(dia, indice, bloque_id, inicio, fin)
        for indice, dia in enumerate(dias)
        for bloque_id, inicio, fin in definicion
    )


def convertir_ocupaciones(
    ocupaciones: Mapping[str, Sequence[str]],
) -> frozenset[tuple[str, str, str]]:
    """Convierte ``{"D1": ["Lu-B1", ...]}`` en tuplas ``(docente, dia, bloque)``."""
    resultado: set[tuple[str, str, str]] = set()
    for docente, claves in ocupaciones.items():
        for clave in claves:
            partes = clave.split("-")
            if len(partes) != 2 or not all(partes):
                raise ValueError(f"Clave de ocupación mal formada: {clave!r}.")
            resultado.add((docente, partes[0], partes[1]))
    return frozenset(resultado)


def crear_escenario(
    nombre: str,
    descripcion: str,
    materias: Sequence[Materia],
    ocupaciones: Mapping[str, Sequence[str]],
    dias: Sequence[str] = DIAS,
    definicion_bloques: Sequence[tuple[str, str, str]] = DEFINICION_BLOQUES,
) -> Escenario:
    """Construye y valida un escenario de cualquier tamaño."""
    materias = tuple(materias)
    escenario = Escenario(
        nombre=nombre,
        descripcion=descripcion,
        grupo=GRUPO_OBJETIVO,
        aula=AULA_DEL_GRUPO,
        materias=materias,
        sesiones=generar_sesiones(materias),
        bloques=crear_bloques(dias, definicion_bloques),
        ocupaciones_docentes=convertir_ocupaciones(ocupaciones),
    )
    escenario.validar_integridad()
    return escenario


OCUPACIONES_CASO_BASE: dict[str, tuple[str, ...]] = {
    "D1": ("Lu-B1", "Mi-B3", "Ju-B3", "Vi-B1", "Vi-B4"),
    "D2": ("Lu-B4", "Mi-B2", "Vi-B1", "Vi-B2", "Vi-B4"),
    "D3": ("Lu-B2", "Lu-B3", "Mi-B1", "Ju-B3", "Ju-B4"),
    "D4": ("Lu-B4", "Mi-B1", "Ju-B2", "Ju-B3"),
    "D5": ("Ma-B4", "Mi-B1", "Ju-B3", "Vi-B3"),
    "D6": ("Mi-B1", "Mi-B4", "Ju-B1", "Vi-B2"),
    "D7": ("Lu-B4", "Ju-B2", "Ju-B3", "Ju-B4"),
}


def crear_caso_base() -> Escenario:
    """Caso 1 — Base: ocupaciones moderadas de los siete docentes."""
    return crear_escenario(
        nombre="Caso 1 — Base",
        descripcion=(
            "Ocupaciones moderadas de los siete docentes con otros grupos. "
            "Funcionamiento normal del algoritmo."
        ),
        materias=crear_materias(),
        ocupaciones=OCUPACIONES_CASO_BASE,
    )


# Casos 2 (docente restringido), 3 (séptimos saturados) y 4 (sin solución)
# se agregan aquí al calibrarlos con la búsqueda implementada.
ESCENARIOS: dict[str, Callable[[], Escenario]] = {
    "base": crear_caso_base,
}
