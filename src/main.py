"""Punto de entrada. Ejecutar desde la raíz del proyecto: ``python -m src.main``."""

from __future__ import annotations

import sys


def main() -> int:
    """Abre la interfaz gráfica; devuelve 1 si Tkinter no está disponible."""
    try:
        from .interfaz import main as abrir_interfaz
    except ImportError:
        print(
            "No se pudo abrir la interfaz: Tkinter no está disponible en este "
            "Python. En Windows, reinstala Python con el instalador oficial y "
            "marca la opción 'tcl/tk and IDLE'.",
            file=sys.stderr,
        )
        return 1
    abrir_interfaz()
    return 0


if __name__ == "__main__":
    sys.exit(main())
