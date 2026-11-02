"""Gráficas de resultados para el reporte (PNG con matplotlib).

- ``retrocesos_<caso>.png``: retrocesos por nivel del árbol (una por caso).
- ``comparacion_casos.png``: paneles con ocupaciones, estados explorados,
  retrocesos y horarios válidos de cada caso, cada uno con su propio eje.

Se usa la API orientada a objetos (``Figure``), sin ventana ni pyplot.
Uso: ``python -m src.graficas`` (escribe en ``salidas/graficas/``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter, MaxNLocator

from .modelo import Escenario
from .resultados import ResumenCaso, resumir

DIRECTORIO_SALIDA = Path("salidas") / "graficas"

# Paleta de referencia (validada): una serie, superficie clara de impresión.
SERIE = "#2a78d6"
SUPERFICIE = "#fcfcfb"
TEXTO = "#0b0b0b"
TEXTO_SECUNDARIO = "#52514e"
TEXTO_TENUE = "#898781"
CUADRICULA = "#e1e0d9"

ANCHO_PULGADAS = 6.5  # ancho útil de una página carta con márgenes de 1 in
DPI = 200


def _figura(alto: float) -> Figure:
    figura = Figure(figsize=(ANCHO_PULGADAS, alto), dpi=DPI, facecolor=SUPERFICIE)
    figura.set_layout_engine("constrained")
    return figura


def _ejes_sobrios(ax, eje_valores: str) -> None:
    """Cuadrícula fina solo en el eje de valores; sin marco salvo la línea base."""
    ax.set_facecolor(SUPERFICIE)
    for lado in ("top", "right", "left", "bottom"):
        ax.spines[lado].set_visible(False)
    base = "bottom" if eje_valores == "y" else "left"
    ax.spines[base].set_visible(True)
    ax.spines[base].set_color(TEXTO_TENUE)
    ax.spines[base].set_linewidth(0.8)
    ax.grid(axis=eje_valores, color=CUADRICULA, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(
        colors=TEXTO_TENUE, labelcolor=TEXTO_SECUNDARIO, labelsize=8, length=0
    )


def _barras(
    figura: Figure, ax, posiciones, valores, grosor: float, horizontal: bool
) -> None:
    """Barras delgadas con extremo redondeado (~3 px) y base recta.

    Los límites se fijan antes para convertir píxeles a unidades de datos; el
    redondeo inferior queda bajo la línea base y lo recorta el propio eje.
    """
    largo_eje = (max(valores) if valores else 0) * 1.15 or 1
    if horizontal:
        ax.set_xlim(0, largo_eje)
    else:
        ax.set_ylim(0, largo_eje)
    figura.draw_without_rendering()
    caja_ejes = ax.get_window_extent()
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    radio_px = 3 * DPI / 96
    r_x = radio_px * (x1 - x0) / caja_ejes.width
    r_y = radio_px * (y1 - y0) / caja_ejes.height

    for pos, valor in zip(posiciones, valores):
        if valor <= 0:
            continue
        if horizontal:
            origen, ancho, alto = (-r_x, pos - grosor / 2), valor + r_x, grosor
        else:
            origen, ancho, alto = (pos - grosor / 2, -r_y), grosor, valor + r_y
        ax.add_patch(
            FancyBboxPatch(
                origen,
                ancho,
                alto,
                boxstyle=f"round,pad=0,rounding_size={r_x}",
                mutation_aspect=r_y / r_x,
                facecolor=SERIE,
                edgecolor="none",
            )
        )


def _numero(valor: float, formato: str) -> str:
    return "0" if valor == 0 else formato.format(valor)


def grafica_retrocesos(resumen: ResumenCaso, escenario: Escenario, ruta: Path) -> Path:
    """Columnas de retrocesos por nivel; el eje muestra la sesión de cada nivel."""
    niveles = list(range(len(escenario.sesiones)))
    valores = [resumen.retrocesos_por_nivel.get(n, 0) for n in niveles]

    figura = _figura(2.9)
    ax = figura.add_subplot()
    _ejes_sobrios(ax, "y")
    ax.set_xlim(-0.6, len(niveles) - 0.4)
    _barras(figura, ax, niveles, valores, grosor=0.45, horizontal=False)
    ax.set_xticks(niveles)
    ax.set_xticklabels(
        [f"{n}\n{s.id}" for n, s in zip(niveles, escenario.sesiones)], fontsize=7
    )
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_xlabel(
        "Nivel del árbol (sesión que se intenta colocar)",
        color=TEXTO_SECUNDARIO,
        fontsize=8,
    )

    if any(valores):
        pico = max(niveles, key=lambda n: valores[n])
        ax.annotate(
            f"{valores[pico]:,}",
            (pico, valores[pico]),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            color=TEXTO,
        )
    else:
        ax.text(
            0.5,
            0.5,
            "Sin retrocesos",
            transform=ax.transAxes,
            ha="center",
            color=TEXTO_SECUNDARIO,
            fontsize=9,
        )

    ax.set_title(
        f"Retrocesos por nivel del árbol · total {resumen.retrocesos:,}",
        loc="left",
        fontsize=9,
        color=TEXTO_SECUNDARIO,
    )
    figura.suptitle(
        resumen.nombre, x=0.01, ha="left", fontsize=10, color=TEXTO, fontweight="bold"
    )
    figura.savefig(ruta, facecolor=SUPERFICIE)
    return ruta


def grafica_comparacion(
    resumenes: list[ResumenCaso], escenarios: dict[str, Escenario], ruta: Path
) -> Path:
    """Cuatro paneles (uno por medida, cada uno con su eje) para comparar casos."""
    nombres = [r.nombre.split(" — ")[-1] for r in resumenes]
    medidas = (
        (
            "Ocupaciones de docentes",
            [len(escenarios[r.clave].ocupaciones_docentes) for r in resumenes],
            "{:,.0f}",
        ),
        ("Estados explorados", [r.estados_explorados for r in resumenes], "{:,.0f}"),
        ("Retrocesos", [r.retrocesos for r in resumenes], "{:,.0f}"),
        (
            "Horarios válidos (miles de millones)",
            [r.horarios_validos / 1e9 for r in resumenes],
            "{:,.1f}",
        ),
    )
    figura = _figura(4.6)
    paneles = figura.subplots(2, 2, sharey=True)
    posiciones = list(range(len(resumenes)))[::-1]  # el caso 1 arriba
    for ax, (titulo, valores, formato) in zip(paneles.flat, medidas):
        _ejes_sobrios(ax, "x")
        ax.set_yticks(posiciones)
        ax.set_yticklabels(nombres, fontsize=8)
        ax.set_ylim(-0.6, len(resumenes) - 0.4)
        _barras(figura, ax, posiciones, valores, grosor=0.34, horizontal=True)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
        ax.set_title(titulo, loc="left", fontsize=9, color=TEXTO)
        limite = ax.get_xlim()[1]
        for pos, valor in zip(posiciones, valores):
            ax.text(
                valor + limite * 0.015,
                pos,
                _numero(valor, formato),
                va="center",
                fontsize=8,
                color=TEXTO,
            )
    figura.suptitle(
        "Comparación de los casos",
        x=0.01,
        ha="left",
        fontsize=10,
        color=TEXTO,
        fontweight="bold",
    )
    figura.savefig(ruta, facecolor=SUPERFICIE)
    return ruta


def generar(
    escenarios: dict[str, Callable[[], Escenario]] | None = None,
    directorio: Path = DIRECTORIO_SALIDA,
) -> list[Path]:
    """Genera todas las gráficas y devuelve sus rutas."""
    if escenarios is None:
        from .escenarios import ESCENARIOS as escenarios
    instancias = {clave: crear() for clave, crear in escenarios.items()}
    resumenes = [resumir(clave, esc) for clave, esc in instancias.items()]

    directorio.mkdir(parents=True, exist_ok=True)
    rutas = [
        grafica_retrocesos(
            r, instancias[r.clave], directorio / f"retrocesos_{r.clave}.png"
        )
        for r in resumenes
    ]
    rutas.append(
        grafica_comparacion(resumenes, instancias, directorio / "comparacion_casos.png")
    )
    return rutas


def main() -> None:
    for ruta in generar():
        print(f"Generada: {ruta}")


if __name__ == "__main__":
    main()
