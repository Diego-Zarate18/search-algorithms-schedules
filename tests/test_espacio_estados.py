"""Pruebas del cálculo del espacio de estados."""

import itertools
import math
import unittest

from src.busqueda import AgenteDFS
from src.escenarios import ESCENARIOS, crear_caso_base, crear_escenario
from src.espacio_estados import calcular, horarios_validos
from src.modelo import Asignacion, EstadoHorario, Materia
from src.verificacion import verificar

DOS_BLOQUES = (("B1", "08:00", "10:00"), ("B2", "10:00", "12:00"))


def por_fuerza_bruta(escenario, con_ocupaciones=True):
    """Enumera todos los horarios completos y cuenta los que la verificación avala."""
    if not con_ocupaciones:
        escenario = crear_escenario(
            "sin_ocup",
            "",
            escenario.materias,
            {},
            dias=tuple(dict.fromkeys(b.dia for b in escenario.bloques)),
            definicion_bloques=tuple(
                dict.fromkeys(
                    (b.id, b.hora_inicio, b.hora_fin) for b in escenario.bloques
                )
            ),
        )
    total = 0
    for bloques in itertools.product(escenario.bloques, repeat=len(escenario.sesiones)):
        estado = EstadoHorario()
        for sesion, bloque in zip(escenario.sesiones, bloques):
            estado.agregar(Asignacion(sesion, bloque))
        total += verificar(escenario, estado).valido
    return total


def mini(materias, ocupaciones, dias=("Lu", "Ma", "Mi")):
    return crear_escenario(
        "mini", "", materias, ocupaciones, dias=dias, definicion_bloques=DOS_BLOQUES
    )


class CifrasDelReporteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.espacio = calcular(crear_caso_base())

    def test_nivel_1_sin_restricciones(self):
        self.assertEqual(self.espacio.sin_restricciones, 20**18)

    def test_nivel_2_con_r1(self):
        self.assertEqual(self.espacio.con_r1, math.factorial(20) // math.factorial(2))

    def test_nivel_3_con_r1_r3_r4(self):
        self.assertEqual(self.espacio.con_r1_r3_r4, 24_156_610_560_000)

    def test_nivel_4_horarios_validos_del_caso_base(self):
        self.assertEqual(self.espacio.validos, 149_507_400_888)

    def test_cota_de_nodos(self):
        esperado = sum(math.perm(20, k) for k in range(19))
        self.assertEqual(self.espacio.nodos_con_r1, esperado)

    def test_cada_nivel_reduce_el_anterior(self):
        e = self.espacio
        self.assertGreater(e.sin_restricciones, e.con_r1)
        self.assertGreater(e.con_r1, e.con_r1_r3_r4)
        self.assertGreater(e.con_r1_r3_r4, e.validos)


class HorariosValidosPorCasoTests(unittest.TestCase):
    """Nivel 4 del espacio de estados para cada caso de resultados."""

    ESPERADO = {
        "base": 149_507_400_888,
        "docente_restringido": 24_255_194_220,
        "septimos_saturados": 116_114_906_919,
        "sin_solucion": 0,
    }

    @classmethod
    def setUpClass(cls):
        cls.conteos = {
            clave: horarios_validos(crear()) for clave, crear in ESCENARIOS.items()
        }

    def test_horarios_validos_de_cada_caso(self):
        self.assertEqual(self.conteos, self.ESPERADO)

    def test_hay_solucion_si_y_solo_si_hay_horarios_validos(self):
        for clave, crear in ESCENARIOS.items():
            with self.subTest(caso=clave):
                encontrado = AgenteDFS(crear(), registrar_eventos=False).resolver()
                self.assertEqual(encontrado.encontrado, self.conteos[clave] > 0)

    def test_el_caso_3_conserva_mas_soluciones_que_el_caso_2(self):
        """Respaldo del hallazgo: más ocupaciones no implica menos soluciones."""
        self.assertGreater(
            self.conteos["septimos_saturados"], 4 * self.conteos["docente_restringido"]
        )


class ConteoContraFuerzaBrutaTests(unittest.TestCase):
    """El conteo por programación dinámica coincide con la enumeración exhaustiva."""

    def comparar(self, escenario):
        for con_ocupaciones in (False, True):
            with self.subTest(con_ocupaciones=con_ocupaciones):
                self.assertEqual(
                    horarios_validos(escenario, con_ocupaciones),
                    por_fuerza_bruta(escenario, con_ocupaciones),
                )

    def test_dos_materias(self):
        materias = (Materia("M1", "A", "D1", (2, 2)), Materia("M2", "B", "D2", (2,)))
        self.comparar(mini(materias, {"D2": ("Lu-B2", "Mi-B1")}))

    def test_materia_con_sesion_de_una_hora(self):
        materias = (Materia("M1", "A", "D1", (2, 2, 1)), Materia("M2", "B", "D2", (2,)))
        self.comparar(mini(materias, {"D1": ("Ma-B1",)}))

    def test_tres_materias(self):
        materias = (
            Materia("M1", "A", "D1", (2, 2)),
            Materia("M2", "B", "D2", (2,)),
            Materia("M3", "C", "D3", (2, 2)),
        )
        self.comparar(mini(materias, {"D3": ("Lu-B1", "Lu-B2")}))

    def test_sin_solucion(self):
        materias = (Materia("M1", "A", "D1", (2, 2, 2)),)
        escenario = mini(materias, {}, dias=("Lu", "Ma"))
        self.assertEqual(horarios_validos(escenario), 0)
        self.assertFalse(AgenteDFS(escenario).resolver().encontrado)


if __name__ == "__main__":
    unittest.main()
