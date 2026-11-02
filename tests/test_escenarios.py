"""Pruebas de los escenarios: el caso base debe coincidir con lo acordado."""

import unittest

from src.escenarios import ESCENARIOS, OCUPACIONES_CASO_BASE, crear_caso_base
from src.modelo import total_horas


class CasoBaseTests(unittest.TestCase):
    def setUp(self):
        self.escenario = crear_caso_base()

    def test_tamano_del_caso_base(self):
        self.assertEqual(len(self.escenario.materias), 7)
        self.assertEqual(len(self.escenario.sesiones), 18)
        self.assertEqual(len(self.escenario.bloques), 20)
        self.assertEqual(total_horas(self.escenario.sesiones), 35)

    def test_horas_por_materia(self):
        self.assertEqual(
            [m.horas_semana for m in self.escenario.materias], [6, 6, 6, 5, 4, 4, 4]
        )

    def test_orden_fijo_de_sesiones(self):
        esperado = [
            f"M{m}.{k}"
            for m, n in [(1, 3), (2, 3), (3, 3), (4, 3), (5, 2), (6, 2), (7, 2)]
            for k in range(1, n + 1)
        ]
        self.assertEqual([s.id for s in self.escenario.sesiones], esperado)

    def test_orden_fijo_de_bloques(self):
        etiquetas = [b.etiqueta for b in self.escenario.bloques]
        self.assertEqual(etiquetas[:5], ["Lu-B1", "Lu-B2", "Lu-B3", "Lu-B4", "Ma-B1"])
        self.assertEqual(etiquetas[-1], "Vi-B4")

    def test_ocupaciones_del_caso_base(self):
        self.assertEqual(len(self.escenario.ocupaciones_docentes), 31)
        self.assertEqual(
            sum(len(v) for v in OCUPACIONES_CASO_BASE.values()), 31
        )
        self.assertTrue(
            self.escenario.docente_ocupado("D1", self.escenario.bloques[0])
        )

    def test_grupo_y_aula_son_descriptivos(self):
        self.assertEqual(self.escenario.grupo, "7° A")
        self.assertEqual(self.escenario.aula, "Aula 7A")

    def test_registro_de_escenarios(self):
        self.assertIn("base", ESCENARIOS)


if __name__ == "__main__":
    unittest.main()
