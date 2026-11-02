"""Pruebas del punto de entrada."""

import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stderr
from unittest import mock

from src.main import main

HAY_TKINTER = importlib.util.find_spec("tkinter") is not None


class MainTests(unittest.TestCase):
    def test_sin_tkinter_avisa_y_devuelve_1(self):
        salida = io.StringIO()
        # Un módulo en None hace que su importación falle con ImportError.
        with mock.patch.dict(sys.modules, {"src.interfaz": None}):
            with redirect_stderr(salida):
                codigo = main()
        self.assertEqual(codigo, 1)
        self.assertIn("Tkinter no está disponible", salida.getvalue())

    @unittest.skipUnless(HAY_TKINTER, "Tkinter no disponible")
    def test_con_tkinter_abre_la_interfaz(self):
        with mock.patch("src.interfaz.main") as abrir:
            self.assertEqual(main(), 0)
        abrir.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
