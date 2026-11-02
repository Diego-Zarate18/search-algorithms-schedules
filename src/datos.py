"""Datos definitivos del escenario de referencia del proyecto."""

from __future__ import annotations

from .modelo import (
    BloqueHorario,
    Escenario,
    Materia,
    Sesion,
)

GRUPO_OBJETIVO = "7A"
AULA_FIJA = "Aula 7A"
DIAS = ("Lu", "Ma", "Mi", "Ju", "Vi")

DEFINICION_BLOQUES = (
    ("B1", "08:00", "10:00"),
    ("B2", "10:00", "12:00"),
    ("B3", "12:00", "14:00"),
    ("B4", "14:00", "16:00"),
)


def crear_materias() -> tuple[Materia, ...]:
    """Crea las siete materias del grupo 7° A."""
    return (
        Materia("M1", "Fundamentos de Inteligencia Artificial", "D1", 6),
        Materia("M2", "Bases de Datos en la Nube (Optativa I)", "D2", 6),
        Materia("M3", "Seguridad Informática", "D3", 6),
        Materia("M4", "Inglés VI", "D4", 5),
        Materia("M5", "Habilidades Gerenciales", "D5", 4),
        Materia("M6", "Formulación de Proyectos de Tecnología", "D6", 4),
        Materia(
            "M7",
            "Ética y Legislación en Tecnologías de la Información",
            "D7",
            4,
        ),
    )


def crear_sesiones(materias: tuple[Materia, ...]) -> tuple[Sesion, ...]:
    """Crea las 18 sesiones en el orden fijo de búsqueda."""
    patrones = {
        "M1": (2, 2, 2),
        "M2": (2, 2, 2),
        "M3": (2, 2, 2),
        "M4": (2, 2, 1),
        "M5": (2, 2),
        "M6": (2, 2),
        "M7": (2, 2),
    }
    sesiones: list[Sesion] = []
    for materia in materias:
        for numero, duracion in enumerate(patrones[materia.id], start=1):
            sesiones.append(
                Sesion(
                    id=f"{materia.id}.{numero}",
                    materia=materia,
                    numero=numero,
                    duracion_horas=duracion,
                )
            )
    return tuple(sesiones)


def crear_bloques() -> tuple[BloqueHorario, ...]:
    """Crea los 20 bloques de la jornada de lunes a viernes."""
    return tuple(
        BloqueHorario(dia, identificador, inicio, fin)
        for dia in DIAS
        for identificador, inicio, fin in DEFINICION_BLOQUES
    )


def crear_ocupaciones_docentes() -> frozenset[tuple[str, str, str]]:
    """Crea las ocupaciones previas de los docentes compartidos."""
    ocupaciones = {
        "D1": ("Lu-B1", "Mi-B3", "Ju-B3", "Vi-B1", "Vi-B4"),
        "D2": ("Lu-B4", "Mi-B2", "Vi-B1", "Vi-B2", "Vi-B4"),
        "D3": ("Lu-B2", "Lu-B3", "Mi-B1", "Ju-B3", "Ju-B4"),
        "D4": ("Lu-B4", "Mi-B1", "Ju-B2", "Ju-B3"),
        "D5": ("Ma-B4", "Mi-B1", "Ju-B3", "Vi-B3"),
        "D6": ("Mi-B1", "Mi-B4", "Ju-B1", "Vi-B2"),
        "D7": ("Lu-B4", "Ju-B2", "Ju-B3", "Ju-B4"),
    }
    return frozenset(
        (docente, dia, bloque)
        for docente, claves in ocupaciones.items()
        for clave in claves
        for dia, bloque in (clave.split("-", maxsplit=1),)
    )


def crear_escenario_base() -> Escenario:
    """Construye y valida el escenario base definitivo."""
    materias = crear_materias()
    escenario = Escenario(
        nombre="base",
        grupo=GRUPO_OBJETIVO,
        aula=AULA_FIJA,
        materias=materias,
        sesiones=crear_sesiones(materias),
        bloques=crear_bloques(),
        ocupaciones_docentes=crear_ocupaciones_docentes(),
    )
    escenario.validar_integridad()
    return escenario
