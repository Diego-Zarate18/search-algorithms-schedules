"""Resumen de resultados por caso, para el reporte.

Ejecuta cada escenario, verifica su horario y guarda en
``salidas/resultados/`` un ``resumen.json`` (datos) y un ``resumen.md``
(tablas listas para copiar al reporte).

Uso: ``python -m src.resultados``
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from .busqueda import AgenteDFS
from .espacio_estados import horarios_validos
from .modelo import Escenario
from .verificacion import verificar

DIRECTORIO_SALIDA = Path("salidas") / "resultados"


@dataclass(frozen=True)
class ResumenCaso:
    clave: str
    nombre: str
    encontrado: bool
    valido: bool
    materias_completas: str
    conflictos: int
    estados_explorados: int
    retrocesos: int
    retrocesos_por_nivel: dict[int, int]
    eventos: int
    tiempo_ms: float
    horarios_validos: int
    horario: dict[str, str]  # etiqueta del bloque -> id de la sesión


def resumir(clave: str, escenario: Escenario) -> ResumenCaso:
    resultado = AgenteDFS(escenario).resolver()
    verificacion = verificar(escenario, resultado.estado)
    metricas = resultado.metricas
    return ResumenCaso(
        clave=clave,
        nombre=escenario.nombre,
        encontrado=resultado.encontrado,
        valido=verificacion.valido,
        materias_completas=(
            f"{verificacion.materias_asignadas}/{verificacion.total_materias}"
        ),
        conflictos=len(verificacion.conflictos),
        estados_explorados=metricas.estados_explorados,
        retrocesos=metricas.retrocesos,
        retrocesos_por_nivel=dict(sorted(metricas.retrocesos_por_nivel.items())),
        eventos=len(resultado.eventos),
        tiempo_ms=round(metricas.tiempo_segundos * 1000, 2),
        horarios_validos=horarios_validos(escenario),
        horario={
            b.etiqueta: a.sesion.id
            for b in escenario.bloques
            if (a := resultado.estado.sesion_en(b)) is not None
        },
    )


def a_markdown(resumenes: list[ResumenCaso], escenarios: dict[str, Escenario]) -> str:
    lineas = [
        "# Resumen de resultados",
        "",
        "| Caso | Solución | Válido | Materias | Explorados | Retrocesos | Eventos "
        "| Horarios válidos | Tiempo (ms) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in resumenes:
        lineas.append(
            f"| {r.nombre} | {'sí' if r.encontrado else 'no'} "
            f"| {'sí' if r.valido else 'no'} | {r.materias_completas} "
            f"| {r.estados_explorados:,} | {r.retrocesos:,} | {r.eventos:,} "
            f"| {r.horarios_validos:,} | {r.tiempo_ms} |"
        )
    lineas += ["", "## Retrocesos por nivel", ""]
    for r in resumenes:
        niveles = " · ".join(f"{k}: {v}" for k, v in r.retrocesos_por_nivel.items())
        lineas.append(f"- **{r.nombre}:** {niveles or 'ninguno'}")
    for r in resumenes:
        if not r.horario:
            continue
        escenario = escenarios[r.clave]
        dias = list(dict.fromkeys(b.dia for b in escenario.bloques))
        ids = list(dict.fromkeys(b.id for b in escenario.bloques))
        encabezado = "| | " + " | ".join(dias) + " |"
        lineas += ["", f"## Horario — {r.nombre}", "", encabezado]
        lineas.append("|---" * (len(dias) + 1) + "|")
        for bloque_id in ids:
            celdas = [r.horario.get(f"{d}-{bloque_id}", "—") for d in dias]
            lineas.append(f"| **{bloque_id}** | " + " | ".join(celdas) + " |")
    return "\n".join(lineas) + "\n"


def exportar(
    escenarios: dict[str, Callable[[], Escenario]] | None = None,
    directorio: Path = DIRECTORIO_SALIDA,
) -> tuple[Path, Path]:
    """Resume todos los escenarios y escribe ``resumen.json`` y ``resumen.md``."""
    if escenarios is None:
        from .escenarios import ESCENARIOS as escenarios
    instancias = {clave: crear() for clave, crear in escenarios.items()}
    resumenes = [resumir(clave, esc) for clave, esc in instancias.items()]

    directorio.mkdir(parents=True, exist_ok=True)
    ruta_json = directorio / "resumen.json"
    ruta_md = directorio / "resumen.md"
    ruta_json.write_text(
        json.dumps([asdict(r) for r in resumenes], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ruta_md.write_text(a_markdown(resumenes, instancias), encoding="utf-8")
    return ruta_json, ruta_md


def main() -> None:
    for ruta in exportar():
        print(f"Generado: {ruta}")


if __name__ == "__main__":
    main()
