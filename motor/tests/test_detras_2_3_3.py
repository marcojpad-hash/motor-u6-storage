#!/usr/bin/env python3
"""Prueba de la corrección 2.3.3 de pregunta detrás v2: 'esta' sin tilde tras preposición/determinante = demostrativo."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motor"))
import plugin_pregunta_detras_v2 as d


def lex(q):
    return [m["lexema"] for m in d.interrogar(q)["marcajes"]]


class TestPreguntaDetras233(unittest.TestCase):
    def test_version(self):
        self.assertIn("2.3.3", str(d.interrogar("¿Qué pasa?")["version"]))

    def test_gcal_esta_calibracion_no_marks(self):
        self.assertNotIn("calibracion", lex("¿Qué configuración dinámica se perfila en Galileo hasta Z90 en esta calibración nueva?"))

    def test_g0926_esta_prueba_no_marks(self):
        self.assertNotIn("prueba", lex("¿Qué configuración dinámica se perfila en Galileo hasta Z90 en esta prueba de resolución?"))

    def test_para_esta_etapa_no_marks(self):
        self.assertNotIn("etapa", lex("¿Qué patrón domina para esta etapa?"))

    def test_ambicioso_still_marks(self):
        self.assertIn("ambicioso", lex("Él era un ambicioso. ¿Qué lo movía?"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
