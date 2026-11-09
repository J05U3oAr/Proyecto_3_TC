"""Integración de la consola con la multiplicadora, incorporada en sesión 3."""
from contextlib import redirect_stdout, redirect_stderr
import io
from pathlib import Path
import unittest
from src.main import main

ROOT = Path(__file__).resolve().parents[1]

class MultiplierCliTests(unittest.TestCase):
    def invoke(self, arguments):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(arguments)
        return code, out.getvalue(), err.getvalue()

    def test_multiplier_all_four_products(self):
        code, out, err = self.invoke([str(ROOT / "examples/multiplicadora.yaml")])
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out.count("Resultado: ACEPTADA"), 4)
        for product in ("110", "1001", "1111", "11001"):
            self.assertIn(f"Cinta final: '{product}'", out)

