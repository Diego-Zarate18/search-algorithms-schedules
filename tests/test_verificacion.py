"""Pruebas de la verificación final independiente."""

import unittest

from src.busqueda import AgenteDFS, TipoEvento
from src.escenarios import crear_caso_base, crear_escenario
from src.modelo import Asignacion, BloqueHorario, EstadoHorario, Materia
from src.verificacion import Regla, verificar


class VerificacionTests(unittest.TestCase):
    def setUp(self):
        self.escenario = crear_caso_base()
        self.estado = EstadoHorario()
        self.sesiones = {s.id: s for s in self.escenario.sesiones}
        self.bloques = {b.etiqueta: b for b in self.escenario.bloques}

    def asignar(self, sesion_id, etiqueta):
        self.estado.agregar(
            Asignacion(self.sesiones[sesion_id], self.bloques[etiqueta])
        )

    def reglas(self):
        return [c.regla for c in verificar(self.escenario, self.estado).conflictos]

    def test_la_solucion_del_caso_base_es_valida(self):
        resultado = AgenteDFS(self.escenario).resolver()
        verificacion = verificar(self.escenario, resultado.estado)
        self.assertTrue(verificacion.valido)
        self.assertEqual(verificacion.sesiones_asignadas, 18)
        self.assertEqual(verificacion.materias_asignadas, 7)
        self.assertEqual(verificacion.total_materias, 7)
        self.assertEqual(verificacion.conflictos, ())

    def test_horario_vacio_no_tiene_conflictos_pero_no_es_valido(self):
        verificacion = verificar(self.escenario, self.estado)
        self.assertFalse(verificacion.valido)
        self.assertEqual(len(verificacion.sesiones_faltantes), 18)
        self.assertEqual(verificacion.materias_asignadas, 0)
        self.assertEqual(verificacion.conflictos, ())

    def test_materia_parcial_no_cuenta_como_asignada(self):
        self.asignar("M5.1", "Lu-B2")
        self.asignar("M6.1", "Lu-B3")
        self.asignar("M6.2", "Ma-B1")
        self.assertEqual(verificar(self.escenario, self.estado).materias_asignadas, 1)

    def test_detecta_r1(self):
        self.asignar("M1.1", "Ma-B1")
        self.asignar("M2.1", "Ma-B1")
        conflicto, = verificar(self.escenario, self.estado).conflictos
        self.assertEqual(conflicto.regla, Regla.R1)
        self.assertEqual(conflicto.sesiones, ("M1.1", "M2.1"))

    def test_detecta_r2(self):
        self.asignar("M1.1", "Lu-B1")  # D1 está ocupado el lunes en B1.
        self.assertEqual(self.reglas(), [Regla.R2])

    def test_detecta_r3(self):
        self.asignar("M1.1", "Ma-B1")
        self.asignar("M1.2", "Ma-B3")
        self.assertIn(Regla.R3, self.reglas())

    def test_detecta_r4_sin_confundirla_con_r3(self):
        self.asignar("M1.1", "Mi-B2")
        self.asignar("M1.2", "Ma-B1")
        self.assertEqual(self.reglas(), [Regla.R4])

    def test_la_sesion_de_una_hora_de_ingles_no_genera_r4(self):
        self.asignar("M4.1", "Ma-B1")
        self.asignar("M4.2", "Mi-B2")
        self.asignar("M4.3", "Lu-B2")
        self.assertEqual(self.reglas(), [])

    def test_reporta_cada_conflicto_por_separado(self):
        self.asignar("M1.1", "Lu-B1")  # R2
        self.asignar("M2.1", "Lu-B1")  # R1 con M1.1
        self.asignar("M3.1", "Mi-B2")
        self.asignar("M3.2", "Ma-B1")  # R4
        self.assertCountEqual(self.reglas(), [Regla.R1, Regla.R2, Regla.R4])

    def test_detecta_asignaciones_ajenas_al_escenario(self):
        ajeno = BloqueHorario("Sa", 5, "B1", "08:00", "10:00")
        self.estado.agregar(Asignacion(self.sesiones["M1.1"], ajeno))
        verificacion = verificar(self.escenario, self.estado)
        self.assertEqual([c.regla for c in verificacion.conflictos], [Regla.INTEGRIDAD])
        self.assertIn("M1.1", verificacion.sesiones_faltantes)

    def test_detecta_una_solucion_alterada(self):
        resultado = AgenteDFS(self.escenario).resolver()
        estado = resultado.estado
        # Mover M1.1 (Lu-B2) al bloque de M2.1 (Lu-B1): choca R1 y R2.
        estado.remover(self.sesiones["M1.1"])
        estado.agregar(Asignacion(self.sesiones["M1.1"], self.bloques["Lu-B1"]))
        reglas = [c.regla for c in verificar(self.escenario, estado).conflictos]
        self.assertCountEqual(reglas, [Regla.R1, Regla.R2])

    def test_todos_los_estados_intermedios_de_la_busqueda_son_consistentes(self):
        """Comprobación cruzada: lo que el agente acepta, la verificación lo avala."""
        resultado = AgenteDFS(self.escenario).resolver()
        estado = EstadoHorario()
        for evento in resultado.eventos:
            if evento.tipo is TipoEvento.ACEPTAR:
                estado.agregar(Asignacion(evento.sesion, evento.bloque))
                self.assertEqual(verificar(self.escenario, estado).conflictos, ())
            elif evento.tipo is TipoEvento.RETROCEDER:
                estado.remover(evento.sesion)
        self.assertTrue(verificar(self.escenario, estado).valido)

    def test_escenario_sin_solucion_queda_vacio(self):
        materias = (Materia("M1", "Materia A", "D1", (2, 2, 2)),)
        escenario = crear_escenario("x", "x", materias, {}, dias=("Lu", "Ma"))
        resultado = AgenteDFS(escenario).resolver()
        verificacion = verificar(escenario, resultado.estado)
        self.assertFalse(resultado.encontrado)
        self.assertFalse(verificacion.valido)
        self.assertEqual(verificacion.sesiones_faltantes, ("M1.1", "M1.2", "M1.3"))


if __name__ == "__main__":
    unittest.main()
