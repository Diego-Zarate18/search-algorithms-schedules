"""Pruebas de las entidades y de la validación de integridad de escenarios."""

import unittest
from dataclasses import replace

from src.escenarios import crear_caso_base, crear_escenario
from src.modelo import Asignacion, EstadoHorario, Materia


def escenario_mini(ocupaciones=None):
    """Escenario reducido (2 materias, 2 días) como los de las trazas manuales."""
    materias = (
        Materia("M1", "Materia A", "D1", (2, 2)),
        Materia("M2", "Materia B", "D2", (2,)),
    )
    return crear_escenario(
        "mini", "Escenario de prueba", materias, ocupaciones or {}, dias=("Lu", "Ma")
    )


class MateriaYSesionesTests(unittest.TestCase):
    def test_horas_se_derivan_de_las_duraciones(self):
        self.assertEqual(Materia("M4", "Inglés VI", "D4", (2, 2, 1)).horas_semana, 5)

    def test_bloques_conocen_el_indice_de_su_dia(self):
        bloques = crear_caso_base().bloques
        self.assertEqual([b.indice_dia for b in bloques[::4]], [0, 1, 2, 3, 4])
        self.assertEqual(bloques[5].etiqueta, "Ma-B2")


class EstadoHorarioTests(unittest.TestCase):
    def setUp(self):
        self.escenario = crear_caso_base()
        self.estado = EstadoHorario()

    def test_agregar_y_remover(self):
        sesion, bloque = self.escenario.sesiones[0], self.escenario.bloques[0]
        self.estado.agregar(Asignacion(sesion, bloque))
        self.assertTrue(self.estado.contiene(sesion))
        self.assertEqual(self.estado.sesion_en(bloque).sesion, sesion)
        self.estado.remover(sesion)
        self.assertEqual(self.estado.cantidad, 0)
        self.assertIsNone(self.estado.sesion_en(bloque))

    def test_una_sesion_no_se_asigna_dos_veces(self):
        sesion = self.escenario.sesiones[0]
        self.estado.agregar(Asignacion(sesion, self.escenario.bloques[0]))
        with self.assertRaises(ValueError):
            self.estado.agregar(Asignacion(sesion, self.escenario.bloques[1]))

    def test_el_estado_no_aplica_reglas_del_problema(self):
        """R1 vive en restricciones.py; el estado no la duplica."""
        bloque = self.escenario.bloques[0]
        primera, segunda = self.escenario.sesiones[:2]
        self.estado.agregar(Asignacion(primera, bloque))
        self.estado.agregar(Asignacion(segunda, bloque))
        self.assertEqual(self.estado.cantidad, 2)

    def test_asignacion_no_tiene_aula(self):
        self.assertNotIn("aula", Asignacion.__dataclass_fields__)


class IntegridadTests(unittest.TestCase):
    def test_acepta_escenarios_mini(self):
        escenario = escenario_mini({"D1": ["Lu-B1"]})
        self.assertEqual(len(escenario.sesiones), 3)
        self.assertEqual(len(escenario.bloques), 8)

    def test_rechaza_ocupacion_en_bloque_inexistente(self):
        with self.assertRaises(ValueError):
            escenario_mini({"D1": ["Lu-B5"]})

    def test_rechaza_ocupacion_en_dia_fuera_del_escenario(self):
        with self.assertRaises(ValueError):
            escenario_mini({"D1": ["Vi-B1"]})

    def test_rechaza_docente_inexistente(self):
        with self.assertRaises(ValueError):
            escenario_mini({"D8": ["Lu-B1"]})

    def test_rechaza_clave_mal_formada(self):
        with self.assertRaises(ValueError):
            escenario_mini({"D1": ["LuB1"]})

    def test_rechaza_sesiones_inconsistentes(self):
        base = crear_caso_base()
        with self.assertRaises(ValueError):
            replace(base, sesiones=base.sesiones[:-1]).validar_integridad()

    def test_rechaza_sesion_mayor_a_un_bloque(self):
        materias = (Materia("M1", "Larga", "D1", (3,)),)
        with self.assertRaises(ValueError):
            crear_escenario("x", "x", materias, {})


if __name__ == "__main__":
    unittest.main()
