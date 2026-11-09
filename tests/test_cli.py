"""Pruebas de la consola conectada con el motor real."""

from contextlib import redirect_stdout, redirect_stderr
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from src.main import main


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def invoke(self, arguments):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(arguments)
        return code, out.getvalue(), err.getvalue()

    def test_recognizer_all_four_inputs_and_full_history(self):
        code, out, err = self.invoke([str(ROOT / "examples/reconocedora.yaml")])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out.count("Resultado: ACEPTADA"), 2)
        self.assertEqual(out.count("Resultado: RECHAZADA"), 2)
        self.assertEqual(out.count("Paso 0 |"), 4)
        self.assertEqual(out.count("Cinta final:"), 4)

    def test_zero_budget_interrupts_each_input(self):
        code, out, _ = self.invoke([str(ROOT / "examples/reconocedora.yaml"), "--max-steps", "0"])
        self.assertEqual(code, 1)
        self.assertEqual(out.count("INTERRUMPIDA POR LÍMITE DE PASOS"), 4)
        self.assertEqual(out.count("Paso 0 |"), 4)

    def test_missing_file(self):
        code, out, err = self.invoke([str(ROOT / "no-existe.yaml")])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("Error:", err)

    def test_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.yaml"
            path.write_text("mt: [", encoding="utf-8")
            code, _, err = self.invoke([str(path)])
        self.assertEqual(code, 2)
        self.assertIn("Error:", err)

    def test_invalid_budget(self):
        for value in ("-1", "1.5", "abc"):
            with self.subTest(value=value), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    main(["unused.yaml", "--max-steps", value])
                self.assertEqual(caught.exception.code, 2)

    def test_module_entrypoint_from_other_directory(self):
        env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONIOENCODING="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            process = subprocess.run([sys.executable, "-m", "src.main", str(ROOT / "examples/base.yaml")],
                                     cwd=directory, env=env, capture_output=True, encoding="utf-8", timeout=30)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.count("Resultado: ACEPTADA"), 3)
