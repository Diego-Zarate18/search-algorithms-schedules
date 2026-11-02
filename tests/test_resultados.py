"""Pruebas del resumen de resultados."""

import json
import tempfile
import unittest
from pathlib import Path

from src.escenarios import crear_caso_base
from src.resultados import exportar, resumir


class ResumenTests(unittest.TestCase):
    def test_resumen_del_caso_base(self):
        r = resumir("base", crear_caso_base())
        self.assertTrue(r.encontrado)
        self.assertTrue(r.valido)
        self.assertEqual(r.materias_completas, "7/7")
        self.assertEqual(r.conflictos, 0)
        self.assertEqual((r.estados_explorados, r.retrocesos), (1834, 83))
        self.assertEqual(r.retrocesos_por_nivel, {12: 1, 13: 3, 14: 16, 15: 21, 16: 42})
        self.assertEqual(r.eventos, 3752)
        self.assertEqual(r.horarios_validos, 149_507_400_888)
        self.assertEqual(len(r.horario), 18)
        self.assertEqual(r.horario["Lu-B1"], "M2.1")

    def test_exportar_escribe_json_y_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta_json, ruta_md = exportar({"base": crear_caso_base}, Path(tmp))
            datos = json.loads(ruta_json.read_text(encoding="utf-8"))
            texto = ruta_md.read_text(encoding="utf-8")
        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]["clave"], "base")
        self.assertEqual(datos[0]["estados_explorados"], 1834)
        self.assertIn("| Caso 1 — Base | sí | sí | 7/7 | 1,834 | 83 | 3,752", texto)
        self.assertIn("## Horario — Caso 1 — Base", texto)
        self.assertIn("| **B1** | M2.1 | M1.2 | M1.3 | M7.1 | M5.2 |", texto)


if __name__ == "__main__":
    unittest.main()
