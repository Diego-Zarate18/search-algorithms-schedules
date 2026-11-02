"""Pruebas del reproductor de la traza de eventos."""

import unittest

from src.busqueda import AgenteDFS
from src.escenarios import crear_caso_base, crear_escenario
from src.modelo import Materia
from src.reproduccion import Reproductor, describir


def escenario_con_retroceso():
    """Una materia de 2 sesiones en 2 días y un bloque; D1 no puede el martes."""
    return crear_escenario(
        "diminuto",
        "Prueba",
        (Materia("M1", "Materia A", "D1", (2, 2)),),
        {"D1": ["Ma-B1"]},
        dias=("Lu", "Ma"),
        definicion_bloques=(("B1", "08:00", "10:00"),),
    )


class ReproductorCasoBaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resultado = AgenteDFS(crear_caso_base()).resolver()

    def setUp(self):
        self.reproductor = Reproductor(self.resultado)

    def test_estado_inicial(self):
        self.assertEqual(self.reproductor.indice, 0)
        self.assertEqual(self.reproductor.total, 3752)
        self.assertEqual(self.reproductor.colocadas, 0)
        self.assertIsNone(self.reproductor.foco)
        self.assertFalse(self.reproductor.terminado)

    def test_al_final_coincide_con_el_resultado(self):
        self.reproductor.ir_al_final()
        esperado = {
            a.bloque.etiqueta: a.sesion
            for a in self.resultado.estado.asignaciones.values()
        }
        self.assertTrue(self.reproductor.terminado)
        self.assertEqual(self.reproductor.asignaciones, esperado)
        self.assertEqual(self.reproductor.explorados, 1834)
        self.assertEqual(self.reproductor.retrocesos, 83)

    def test_avanzar_no_pasa_del_final(self):
        aplicados = self.reproductor.avanzar(10_000)
        self.assertEqual(aplicados, 3752)
        self.assertEqual(self.reproductor.avanzar(), 0)

    def test_retroceder_equivale_a_reproducir_hasta_ese_punto(self):
        self.reproductor.ir_a(2000)
        self.reproductor.retroceder(500)
        otro = Reproductor(self.resultado)
        otro.avanzar(1500)
        self.assertEqual(self.reproductor.indice, 1500)
        self.assertEqual(self.reproductor.asignaciones, otro.asignaciones)
        self.assertEqual(self.reproductor.explorados, otro.explorados)
        self.assertEqual(self.reproductor.retrocesos, otro.retrocesos)
        self.assertEqual(list(self.reproductor.bitacora), list(otro.bitacora))

    def test_ir_a_limita_el_rango(self):
        self.reproductor.ir_a(-5)
        self.assertEqual(self.reproductor.indice, 0)
        self.reproductor.ir_a(10**6)
        self.assertEqual(self.reproductor.indice, 3752)

    def test_bitacora_tiene_tamano_maximo(self):
        reproductor = Reproductor(self.resultado, tam_bitacora=50)
        reproductor.ir_al_final()
        self.assertEqual(len(reproductor.bitacora), 50)
        self.assertIn("Solución encontrada", reproductor.bitacora[-1])


class DescripcionTests(unittest.TestCase):
    def test_traza_con_retroceso_y_sin_solucion(self):
        resultado = AgenteDFS(escenario_con_retroceso()).resolver()
        self.assertEqual(
            [describir(e) for e in resultado.eventos],
            [
                "Probar M1.1 en Lu-B1",
                "Aceptar M1.1 en Lu-B1",
                "Probar M1.2 en Lu-B1",
                "Rechazar M1.2 en Lu-B1 · "
                "R1: el grupo ya tiene una sesión en ese bloque",
                "Probar M1.2 en Ma-B1",
                "Rechazar M1.2 en Ma-B1 · R2: el docente está ocupado con otro grupo",
                "Retroceder: quitar M1.1 de Lu-B1",
                "Probar M1.1 en Ma-B1",
                "Rechazar M1.1 en Ma-B1 · R2: el docente está ocupado con otro grupo",
                "No existe solución: se agotaron todas las alternativas",
            ],
        )

    def test_descripcion_breve_abrevia_el_motivo(self):
        resultado = AgenteDFS(escenario_con_retroceso()).resolver()
        rechazo = resultado.eventos[3]
        self.assertEqual(describir(rechazo, breve=True), "Rechazar M1.2 en Lu-B1 · R1")

    def test_la_bitacora_numera_los_pasos(self):
        resultado = AgenteDFS(escenario_con_retroceso()).resolver()
        reproductor = Reproductor(resultado)
        reproductor.avanzar(2)
        self.assertEqual(
            list(reproductor.bitacora),
            ["     1  Probar M1.1 en Lu-B1", "     2  Aceptar M1.1 en Lu-B1"],
        )


if __name__ == "__main__":
    unittest.main()
