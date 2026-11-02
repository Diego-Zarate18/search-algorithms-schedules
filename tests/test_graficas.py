"""Pruebas de las gráficas: se omiten si matplotlib no está instalado."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

HAY_MATPLOTLIB = importlib.util.find_spec("matplotlib") is not None
FIRMA_PNG = b"\x89PNG\r\n\x1a\n"


@unittest.skipUnless(HAY_MATPLOTLIB, "matplotlib no instalado")
class GraficasTests(unittest.TestCase):
    def test_genera_una_grafica_por_caso_y_la_comparacion(self):
        from src.escenarios import crear_caso_base, crear_caso_sin_solucion
        from src.graficas import generar

        escenarios = {"base": crear_caso_base, "sin_solucion": crear_caso_sin_solucion}
        with tempfile.TemporaryDirectory() as tmp:
            rutas = generar(escenarios, Path(tmp))
            nombres = [r.name for r in rutas]
            firmas = [r.read_bytes()[:8] for r in rutas]
        self.assertEqual(
            nombres,
            [
                "retrocesos_base.png",
                "retrocesos_sin_solucion.png",
                "comparacion_casos.png",
            ],
        )
        self.assertTrue(all(f == FIRMA_PNG for f in firmas))

    def test_caso_sin_retrocesos(self):
        from src.escenarios import crear_mini_sin_retroceso
        from src.graficas import grafica_retrocesos
        from src.resultados import resumir

        escenario = crear_mini_sin_retroceso()
        resumen = resumir("mini_sin_retroceso", escenario)
        self.assertEqual(resumen.retrocesos, 0)
        with tempfile.TemporaryDirectory() as tmp:
            ruta = grafica_retrocesos(resumen, escenario, Path(tmp) / "mini.png")
            self.assertEqual(ruta.read_bytes()[:8], FIRMA_PNG)


if __name__ == "__main__":
    unittest.main()
