"""Escenarios (casos) del proyecto.

Los cuatro casos de resultados comparten materias, días y bloques; solo
cambian las ocupaciones de los docentes con otros grupos. Sus resultados
de referencia están fijados en ``tests/test_escenarios.py`` y explicados
en ``docs/decisiones_tecnicas.md`` (sección 5).
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


def bloques_excepto(dias_libres: Sequence[str]) -> tuple[str, ...]:
    """Etiquetas de todos los bloques salvo los de ``dias_libres``.

    Sirve para describir a un docente que solo está disponible ciertos días.
    """
    return tuple(
        f"{dia}-{bloque_id}"
        for dia in DIAS
        if dia not in dias_libres
        for bloque_id, _, _ in DEFINICION_BLOQUES
    )


OCUPACIONES_CASO_BASE: dict[str, tuple[str, ...]] = {
    "D1": ("Lu-B1", "Mi-B3", "Ju-B3", "Vi-B1", "Vi-B4"),
    "D2": ("Lu-B4", "Mi-B2", "Vi-B1", "Vi-B2", "Vi-B4"),
    "D3": ("Lu-B2", "Lu-B3", "Mi-B1", "Ju-B3", "Ju-B4"),
    "D4": ("Lu-B4", "Mi-B1", "Ju-B2", "Ju-B3"),
    "D5": ("Ma-B4", "Mi-B1", "Ju-B3", "Vi-B3"),
    "D6": ("Mi-B1", "Mi-B4", "Ju-B1", "Vi-B2"),
    "D7": ("Lu-B4", "Ju-B2", "Ju-B3", "Ju-B4"),
}

# Caso 2: igual que el base, pero D6 (Formulación, penúltima materia en el
# orden de búsqueda) solo está disponible martes y jueves.
OCUPACIONES_CASO_DOCENTE_RESTRINGIDO: dict[str, tuple[str, ...]] = {
    **OCUPACIONES_CASO_BASE,
    "D6": bloques_excepto(("Ma", "Ju")),
}

# Caso 3: cada docente imparte su materia también a 7° B y 7° C. Las
# ocupaciones provienen de horarios válidos generados para esos dos grupos
# (sin choques de docente entre ellos), por eso cada docente queda ocupado
# el doble de sesiones de su materia.
OCUPACIONES_CASO_SEPTIMOS_SATURADOS: dict[str, tuple[str, ...]] = {
    "D1": ("Lu-B3", "Ma-B4", "Mi-B3", "Mi-B4", "Ju-B1", "Vi-B1"),
    "D2": ("Lu-B1", "Ma-B2", "Ju-B1", "Ju-B2", "Vi-B2", "Vi-B3"),
    "D3": ("Lu-B2", "Ma-B3", "Mi-B2", "Mi-B3", "Ju-B3", "Vi-B3"),
    "D4": ("Lu-B2", "Lu-B4", "Ma-B1", "Mi-B1", "Ju-B3", "Vi-B4"),
    "D5": ("Lu-B1", "Ma-B1", "Ma-B3", "Mi-B2"),
    "D6": ("Lu-B3", "Ma-B4", "Ju-B4", "Vi-B4"),
    "D7": ("Ma-B2", "Ju-B4", "Vi-B1", "Vi-B2"),
}

# Caso 4: igual que el base, pero D1 (IA) solo está disponible martes y
# jueves. IA necesita 3 sesiones en días distintos (R3): no hay solución.
OCUPACIONES_CASO_SIN_SOLUCION: dict[str, tuple[str, ...]] = {
    **OCUPACIONES_CASO_BASE,
    "D1": bloques_excepto(("Ma", "Ju")),
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


def crear_caso_docente_restringido() -> Escenario:
    """Caso 2 — Docente restringido: D6 solo puede martes y jueves."""
    return crear_escenario(
        nombre="Caso 2 — Docente restringido",
        descripcion=(
            "El docente de Formulación de Proyectos (D6) solo está disponible "
            "martes y jueves. Como esa materia se programa casi al final, el "
            "agente descubre el conflicto tarde y retrocede mucho más."
        ),
        materias=crear_materias(),
        ocupaciones=OCUPACIONES_CASO_DOCENTE_RESTRINGIDO,
    )


def crear_caso_septimos_saturados() -> Escenario:
    """Caso 3 — Séptimos saturados: docentes compartidos con 7° B y 7° C."""
    return crear_escenario(
        nombre="Caso 3 — Séptimos saturados",
        descripcion=(
            "Cada docente imparte su materia también a 7° B y 7° C. Hay más "
            "ocupaciones que en el caso base, pero bien repartidas: el agente "
            "descarta antes las opciones malas y retrocede menos."
        ),
        materias=crear_materias(),
        ocupaciones=OCUPACIONES_CASO_SEPTIMOS_SATURADOS,
    )


def crear_caso_sin_solucion() -> Escenario:
    """Caso 4 — Sin solución: D1 solo puede 2 días e IA necesita 3."""
    return crear_escenario(
        nombre="Caso 4 — Sin solución",
        descripcion=(
            "El docente de IA (D1) solo está disponible martes y jueves, pero "
            "IA necesita tres sesiones en días distintos. El agente agota las "
            "alternativas y reporta que no existe solución."
        ),
        materias=crear_materias(),
        ocupaciones=OCUPACIONES_CASO_SIN_SOLUCION,
    )


ESCENARIOS: dict[str, Callable[[], Escenario]] = {
    "base": crear_caso_base,
    "docente_restringido": crear_caso_docente_restringido,
    "septimos_saturados": crear_caso_septimos_saturados,
    "sin_solucion": crear_caso_sin_solucion,
}
