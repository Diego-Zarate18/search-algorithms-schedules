"""Pruebas del agente DFS con retroceso."""

import unittest
from collections import Counter

from src.busqueda import AgenteDFS, TipoEvento
from src.escenarios import crear_caso_base, crear_escenario
from src.modelo import Materia
from src.restricciones import MotivoRechazo

# Resultado de referencia del caso 1 (docs/decisiones_tecnicas.md, sección 3.8).
HORARIO_CASO_BASE = {
    "Lu-B1": "M2.1", "Ma-B1": "M1.2", "Mi-B1": "M1.3", "Ju-B1": "M7.1", "Vi-B1": "M5.2",
    "Lu-B2": "M1.1", "Ma-B2": "M2.2", "Mi-B2": "M3.3", "Ju-B2": "M5.1", "Vi-B2": "M7.2",
    "Lu-B3": "M4.1", "Ma-B3": "M3.2", "Mi-B3": "M2.3", "Ju-B3": "M6.1", "Vi-B3": "M6.2",
    "Lu-B4": "M3.1", "Ma-B4": "M4.2", "Mi-B4": "M4.3",
}

UN_BLOQUE_POR_DIA = (("B1", "08:00", "10:00"),)


def escenario_diminuto(ocupaciones):
    """Una materia de 2 sesiones, 2 días y un bloque por día."""
    return crear_escenario(
        "diminuto",
        "Prueba",
        (Materia("M1", "Materia A", "D1", (2, 2)),),
        ocupaciones,
        dias=("Lu", "Ma"),
        definicion_bloques=UN_BLOQUE_POR_DIA,
    )


def resumir(eventos):
    """Eventos como tuplas legibles para comparar secuencias exactas."""
    return [
        (
            e.tipo.value,
            e.sesion.id if e.sesion else None,
            e.bloque.etiqueta if e.bloque else None,
            e.motivo.name if e.motivo else None,
        )
        for e in eventos
    ]


class CasoBaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resultado = AgenteDFS(crear_caso_base()).resolver()

    def test_encuentra_solucion_completa(self):
        self.assertTrue(self.resultado.encontrado)
        self.assertEqual(self.resultado.estado.cantidad, 18)

    def test_reproduce_las_metricas_de_referencia(self):
        metricas = self.resultado.metricas
        self.assertEqual(metricas.estados_explorados, 1834)
        self.assertEqual(metricas.retrocesos, 83)
        self.assertEqual(
            metricas.retrocesos_por_nivel, {12: 1, 13: 3, 14: 16, 15: 21, 16: 42}
        )
        self.assertGreater(metricas.tiempo_segundos, 0)

    def test_reproduce_el_horario_de_referencia(self):
        horario = {
            a.bloque.etiqueta: a.sesion.id
            for a in self.resultado.estado.asignaciones.values()
        }
        self.assertEqual(horario, HORARIO_CASO_BASE)

    def test_eventos_son_coherentes_con_las_metricas(self):
        conteo = Counter(e.tipo for e in self.resultado.eventos)
        metricas = self.resultado.metricas
        self.assertEqual(conteo[TipoEvento.PROBAR], metricas.estados_explorados)
        self.assertEqual(conteo[TipoEvento.RETROCEDER], metricas.retrocesos)
        self.assertEqual(
            conteo[TipoEvento.PROBAR],
            conteo[TipoEvento.ACEPTAR] + conteo[TipoEvento.RECHAZAR],
        )
        self.assertEqual(conteo[TipoEvento.ACEPTAR] - conteo[TipoEvento.RETROCEDER], 18)
        self.assertEqual(conteo[TipoEvento.SOLUCION], 1)
        self.assertEqual(self.resultado.eventos[-1].tipo, TipoEvento.SOLUCION)

    def test_cada_prueba_va_seguida_de_su_veredicto(self):
        eventos = self.resultado.eventos
        for i, evento in enumerate(eventos):
            if evento.tipo is not TipoEvento.PROBAR:
                continue
            veredicto = eventos[i + 1]
            self.assertIn(veredicto.tipo, (TipoEvento.ACEPTAR, TipoEvento.RECHAZAR))
            self.assertEqual(
                (veredicto.sesion, veredicto.bloque), (evento.sesion, evento.bloque)
            )
            self.assertEqual(
                veredicto.motivo is not None, veredicto.tipo is TipoEvento.RECHAZAR
            )

    def test_la_busqueda_es_determinista(self):
        otro = AgenteDFS(crear_caso_base()).resolver()
        self.assertEqual(otro.eventos, self.resultado.eventos)


class AgenteTests(unittest.TestCase):
    def test_resolver_dos_veces_reinicia_la_busqueda(self):
        agente = AgenteDFS(escenario_diminuto({}))
        primero, segundo = agente.resolver(), agente.resolver()
        self.assertEqual(primero.eventos, segundo.eventos)
        self.assertEqual(segundo.metricas.estados_explorados, 3)
        self.assertIsNot(primero.estado, segundo.estado)

    def test_sin_registro_de_eventos_mantiene_las_metricas(self):
        resultado = AgenteDFS(crear_caso_base(), registrar_eventos=False).resolver()
        self.assertEqual(resultado.eventos, ())
        self.assertEqual(resultado.metricas.estados_explorados, 1834)
        self.assertEqual(resultado.metricas.retrocesos, 83)

    def test_traza_exacta_sin_retroceso(self):
        resultado = AgenteDFS(escenario_diminuto({})).resolver()
        self.assertEqual(
            resumir(resultado.eventos),
            [
                ("probar", "M1.1", "Lu-B1", None),
                ("aceptar", "M1.1", "Lu-B1", None),
                ("probar", "M1.2", "Lu-B1", None),
                ("rechazar", "M1.2", "Lu-B1", "BLOQUE_OCUPADO_POR_GRUPO"),
                ("probar", "M1.2", "Ma-B1", None),
                ("aceptar", "M1.2", "Ma-B1", None),
                ("solucion", None, None, None),
            ],
        )

    def test_traza_exacta_con_retroceso_y_sin_solucion(self):
        # D1 no puede el martes: M1.2 no cabe, se deshace M1.1 y se agota el árbol.
        resultado = AgenteDFS(escenario_diminuto({"D1": ["Ma-B1"]})).resolver()
        self.assertFalse(resultado.encontrado)
        self.assertEqual(resultado.estado.cantidad, 0)
        self.assertEqual(resultado.metricas.retrocesos_por_nivel, {0: 1})
        self.assertEqual(
            resumir(resultado.eventos),
            [
                ("probar", "M1.1", "Lu-B1", None),
                ("aceptar", "M1.1", "Lu-B1", None),
                ("probar", "M1.2", "Lu-B1", None),
                ("rechazar", "M1.2", "Lu-B1", "BLOQUE_OCUPADO_POR_GRUPO"),
                ("probar", "M1.2", "Ma-B1", None),
                ("rechazar", "M1.2", "Ma-B1", "DOCENTE_OCUPADO"),
                ("retroceder", "M1.1", "Lu-B1", None),
                ("probar", "M1.1", "Ma-B1", None),
                ("rechazar", "M1.1", "Ma-B1", "DOCENTE_OCUPADO"),
                ("sin_solucion", None, None, None),
            ],
        )

    def test_el_caso_base_ejercita_las_cuatro_restricciones(self):
        resultado = AgenteDFS(crear_caso_base()).resolver()
        motivos = {e.motivo for e in resultado.eventos if e.motivo is not None}
        # En el caso base aparecen los cuatro motivos de rechazo.
        self.assertEqual(motivos, set(MotivoRechazo))


if __name__ == "__main__":
    unittest.main()
