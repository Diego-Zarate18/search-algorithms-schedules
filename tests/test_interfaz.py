"""Prueba de humo de la interfaz: se omite si no hay Tkinter o pantalla."""

import unittest

try:
    import tkinter as tk

    raiz_prueba = tk.Tk()
    raiz_prueba.destroy()
    HAY_PANTALLA = True
except Exception:  # Sin Tkinter instalado o sin servidor gráfico.
    HAY_PANTALLA = False


@unittest.skipUnless(HAY_PANTALLA, "Tkinter o pantalla no disponibles")
class InterfazTests(unittest.TestCase):
    def setUp(self):
        from src.interfaz import Aplicacion

        self.raiz = tk.Tk()
        self.raiz.withdraw()
        self.app = Aplicacion(self.raiz)

    def tearDown(self):
        self.raiz.destroy()

    def test_antes_de_ejecutar_solo_se_puede_ejecutar(self):
        self.assertFalse(self.app.boton_ejecutar.instate(["disabled"]))
        for boton in self.app.botones.values():
            self.assertTrue(boton.instate(["disabled"]))
        self.assertEqual(len(self.app.celdas), 20)

    def test_reproduccion_completa_del_primer_caso(self):
        self.app.ejecutar()
        self.assertTrue(self.app.boton_ejecutar.instate(["disabled"]))
        self.app.paso_siguiente()
        self.assertEqual(self.app.reproductor.indice, 1)
        self.app.ir_al_final()
        self.assertTrue(self.app.reproductor.terminado)
        self.assertIn("Horario válido", self.app.verificacion.cget("text"))
        self.assertTrue(self.app.botones["siguiente"].instate(["disabled"]))
        self.app.reiniciar()
        self.assertEqual(self.app.reproductor.indice, 0)

    def test_el_selector_incluye_los_casos_y_los_mini(self):
        self.assertEqual(len(self.app.combo_caso.cget("values")), 6)

    def test_escenario_mini_con_retroceso(self):
        self.app.combo_caso.current(5)
        self.app.seleccionar_escenario()
        self.assertEqual(len(self.app.celdas), 4)
        self.app.ejecutar()
        self.app.ir_al_final()
        self.assertEqual(self.app.reproductor.total, 26)
        self.assertEqual(self.app.reproductor.retrocesos, 1)
        self.assertIn("Horario válido", self.app.verificacion.cget("text"))

    def test_reproduccion_automatica_avanza(self):
        self.app.ejecutar()
        self.app.velocidad.set(1.0)
        self.app.alternar_reproduccion()
        self.assertTrue(self.app.reproduciendo)
        for _ in range(5):
            self.raiz.after(40)
            self.raiz.update()
        self.assertGreater(self.app.reproductor.indice, 0)
        self.app.alternar_reproduccion()
        self.assertFalse(self.app.reproduciendo)


if __name__ == "__main__":
    unittest.main()
