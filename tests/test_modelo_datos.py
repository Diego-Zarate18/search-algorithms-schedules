import unittest

from src.datos import crear_escenario_base
from src.modelo import EstadoHorario, total_horas


class ModeloDatosTests(unittest.TestCase):
    def setUp(self) -> None:
        self.escenario = crear_escenario_base()

    def test_escenario_tiene_el_tamano_definitivo(self) -> None:
        self.assertEqual(len(self.escenario.materias), 7)
        self.assertEqual(len(self.escenario.sesiones), 18)
        self.assertEqual(len(self.escenario.bloques), 20)
        self.assertEqual(total_horas(self.escenario.sesiones), 35)

    def test_sesiones_estan_en_el_orden_fijo(self) -> None:
        self.assertEqual(
            [sesion.id for sesion in self.escenario.sesiones],
            [
                "M1.1",
                "M1.2",
                "M1.3",
                "M2.1",
                "M2.2",
                "M2.3",
                "M3.1",
                "M3.2",
                "M3.3",
                "M4.1",
                "M4.2",
                "M4.3",
                "M5.1",
                "M5.2",
                "M6.1",
                "M6.2",
                "M7.1",
                "M7.2",
            ],
        )

    def test_estado_no_permite_dos_sesiones_en_un_bloque(self) -> None:
        estado = EstadoHorario()
        bloque = self.escenario.bloques[0]
        primera, segunda = self.escenario.sesiones[:2]

        from src.modelo import Asignacion

        estado.agregar(Asignacion(primera, bloque, self.escenario.aula))

        with self.assertRaises(ValueError):
            estado.agregar(Asignacion(segunda, bloque, self.escenario.aula))


if __name__ == "__main__":
    unittest.main()
