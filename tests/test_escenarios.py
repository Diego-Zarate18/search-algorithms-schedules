"""Pruebas de los escenarios: el caso base debe coincidir con lo acordado."""

import unittest

from src.busqueda import AgenteDFS
from src.escenarios import (
    ESCENARIOS,
    OCUPACIONES_CASO_BASE,
    OCUPACIONES_CASO_DOCENTE_RESTRINGIDO,
    OCUPACIONES_CASO_SEPTIMOS_SATURADOS,
    OCUPACIONES_CASO_SIN_SOLUCION,
    bloques_excepto,
    crear_caso_base,
)
from src.modelo import total_horas
from src.verificacion import verificar

# Resultados de referencia (docs/decisiones_tecnicas.md, sección 5).
REFERENCIA = {
    "base": (True, 1834, 83, {12: 1, 13: 3, 14: 16, 15: 21, 16: 42}),
    "docente_restringido": (
        True, 10611, 522, {10: 1, 11: 9, 12: 55, 13: 97, 14: 284, 15: 19, 16: 57}
    ),
    "septimos_saturados": (True, 692, 26, {13: 2, 14: 8, 15: 6, 16: 10}),
    "sin_solucion": (False, 500, 24, {0: 8, 1: 16}),
}


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



class CasosDeResultadosTests(unittest.TestCase):
    def test_registro_de_los_cuatro_casos(self):
        self.assertEqual(list(ESCENARIOS), list(REFERENCIA))

    def test_los_casos_comparten_materias_y_bloques(self):
        base = crear_caso_base()
        for crear in ESCENARIOS.values():
            escenario = crear()
            self.assertEqual(escenario.materias, base.materias)
            self.assertEqual(escenario.bloques, base.bloques)

    def test_bloques_excepto(self):
        bloques = bloques_excepto(("Ma", "Ju"))
        self.assertEqual(len(bloques), 12)
        self.assertNotIn("Ma-B1", bloques)
        self.assertIn("Lu-B1", bloques)

    def test_ocupaciones_de_cada_caso(self):
        self.assertEqual(
            {**OCUPACIONES_CASO_DOCENTE_RESTRINGIDO, "D6": OCUPACIONES_CASO_BASE["D6"]},
            OCUPACIONES_CASO_BASE,
        )
        self.assertEqual(len(OCUPACIONES_CASO_DOCENTE_RESTRINGIDO["D6"]), 12)
        self.assertEqual(
            {k: len(v) for k, v in OCUPACIONES_CASO_SEPTIMOS_SATURADOS.items()},
            {"D1": 6, "D2": 6, "D3": 6, "D4": 6, "D5": 4, "D6": 4, "D7": 4},
        )
        self.assertEqual(len(OCUPACIONES_CASO_SIN_SOLUCION["D1"]), 12)

    def test_resultados_de_referencia(self):
        for nombre, (encontrado, explorados, retrocesos, niveles) in REFERENCIA.items():
            with self.subTest(caso=nombre):
                escenario = ESCENARIOS[nombre]()
                resultado = AgenteDFS(escenario, registrar_eventos=False).resolver()
                metricas = resultado.metricas
                self.assertEqual(resultado.encontrado, encontrado)
                self.assertEqual(metricas.estados_explorados, explorados)
                self.assertEqual(metricas.retrocesos, retrocesos)
                self.assertEqual(metricas.retrocesos_por_nivel, niveles)
                verificacion = verificar(escenario, resultado.estado)
                self.assertEqual(verificacion.valido, encontrado)

    def test_mas_restricciones_no_implica_mas_retrocesos(self):
        """Hallazgo del caso 3: importa dónde caen las restricciones, no cuántas."""
        def ocupaciones(caso):
            return sum(len(v) for v in caso.values())

        self.assertLess(
            ocupaciones(OCUPACIONES_CASO_SEPTIMOS_SATURADOS),
            ocupaciones(OCUPACIONES_CASO_DOCENTE_RESTRINGIDO),
        )
        self.assertGreater(
            ocupaciones(OCUPACIONES_CASO_SEPTIMOS_SATURADOS),
            ocupaciones(OCUPACIONES_CASO_BASE),
        )
        self.assertLess(REFERENCIA["septimos_saturados"][2], REFERENCIA["base"][2])
        self.assertGreater(REFERENCIA["docente_restringido"][2], REFERENCIA["base"][2])


if __name__ == "__main__":
    unittest.main()
