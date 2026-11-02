"""Pruebas de las restricciones R1–R4."""

import unittest

from src.escenarios import crear_caso_base
from src.modelo import Asignacion, EstadoHorario
from src.restricciones import MotivoRechazo, validar


class RestriccionesTests(unittest.TestCase):
    def setUp(self):
        self.escenario = crear_caso_base()
        self.estado = EstadoHorario()
        self.sesiones = {s.id: s for s in self.escenario.sesiones}
        self.bloques = {b.etiqueta: b for b in self.escenario.bloques}

    def asignar(self, sesion_id, etiqueta):
        self.estado.agregar(
            Asignacion(self.sesiones[sesion_id], self.bloques[etiqueta])
        )

    def validar(self, sesion_id, etiqueta):
        return validar(
            self.escenario,
            self.estado,
            self.sesiones[sesion_id],
            self.bloques[etiqueta],
        )

    def test_candidato_valido_en_estado_vacio(self):
        self.assertIsNone(self.validar("M1.1", "Lu-B2"))

    def test_r1_bloque_ocupado_por_el_grupo(self):
        self.asignar("M2.1", "Ma-B1")
        self.assertEqual(
            self.validar("M1.1", "Ma-B1"), MotivoRechazo.BLOQUE_OCUPADO_POR_GRUPO
        )

    def test_r2_docente_ocupado(self):
        # D1 (IA) da clase a otro grupo el lunes en B1.
        self.assertEqual(self.validar("M1.1", "Lu-B1"), MotivoRechazo.DOCENTE_OCUPADO)

    def test_r2_solo_afecta_al_docente_ocupado(self):
        # Lu-B1 está ocupado para D1, pero no para D2.
        self.assertIsNone(self.validar("M2.1", "Lu-B1"))

    def test_r3_misma_materia_mismo_dia(self):
        self.asignar("M1.1", "Ma-B1")
        self.assertEqual(
            self.validar("M1.2", "Ma-B3"),
            MotivoRechazo.MATERIA_YA_TIENE_SESION_ESE_DIA,
        )

    def test_r3_no_afecta_a_otras_materias(self):
        self.asignar("M1.1", "Ma-B1")
        self.assertIsNone(self.validar("M2.1", "Ma-B3"))

    def test_r4_sesion_en_dia_anterior_a_su_predecesora(self):
        self.asignar("M1.1", "Mi-B2")
        self.assertEqual(
            self.validar("M1.2", "Ma-B1"), MotivoRechazo.VIOLA_ORDEN_DE_SESIONES
        )

    def test_r4_acepta_dia_posterior(self):
        self.asignar("M1.1", "Mi-B2")
        self.assertIsNone(self.validar("M1.2", "Ju-B1"))

    def test_r4_compara_solo_con_la_sesion_inmediata_anterior(self):
        self.asignar("M1.1", "Lu-B2")
        self.asignar("M1.2", "Mi-B2")
        self.assertEqual(
            self.validar("M1.3", "Ma-B2"), MotivoRechazo.VIOLA_ORDEN_DE_SESIONES
        )
        self.assertIsNone(self.validar("M1.3", "Ju-B1"))

    def test_r4_exime_a_la_sesion_de_una_hora_de_ingles(self):
        self.asignar("M4.1", "Ma-B1")
        self.asignar("M4.2", "Mi-B2")
        self.assertIsNone(self.validar("M4.3", "Lu-B1"))

    def test_r4_no_aplica_si_la_anterior_no_esta_asignada(self):
        self.assertIsNone(self.validar("M1.2", "Lu-B2"))

    def test_prioridad_r1_sobre_r2(self):
        # Lu-B1: ocupado por el grupo y, además, D1 está ocupado.
        self.asignar("M2.1", "Lu-B1")
        self.assertEqual(
            self.validar("M1.1", "Lu-B1"), MotivoRechazo.BLOQUE_OCUPADO_POR_GRUPO
        )

    def test_prioridad_r2_sobre_r3(self):
        # Vi-B1: D1 ocupado y M1 ya tiene sesión el viernes.
        self.asignar("M1.1", "Vi-B2")
        self.assertEqual(self.validar("M1.2", "Vi-B1"), MotivoRechazo.DOCENTE_OCUPADO)

    def test_prioridad_r3_sobre_r4(self):
        # Mismo día que la sesión anterior: falla R3 antes que R4.
        self.asignar("M1.1", "Mi-B2")
        self.assertEqual(
            self.validar("M1.2", "Mi-B4"),
            MotivoRechazo.MATERIA_YA_TIENE_SESION_ESE_DIA,
        )

    def test_validar_no_modifica_el_estado(self):
        self.asignar("M1.1", "Mi-B2")
        antes = dict(self.estado.asignaciones)
        self.validar("M1.2", "Ma-B1")
        self.validar("M2.1", "Mi-B2")
        self.assertEqual(self.estado.asignaciones, antes)


if __name__ == "__main__":
    unittest.main()
