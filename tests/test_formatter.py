"""La representación conserva posiciones, blancos e historial completo."""

import unittest

from src.formatter import format_configuration, format_result, tape_text
from src.models import InstantaneousDescription, SimulationResult, SimulationStatus, TapeSnapshot


class FormatterTests(unittest.TestCase):
    def test_empty_tape_shows_blank_at_negative_head(self):
        item = InstantaneousDescription(0, "q0", TapeSnapshot((), -12, "B"))
        text = format_configuration(item)
        self.assertIn("Cabezal: -12", text)
        self.assertIn("'B'", text)
        self.assertIn("^", text)
        self.assertEqual(tape_text(item.tape), "")

    def test_interval_includes_gaps_and_head_outside_content(self):
        tape = TapeSnapshot(((-2, "a"), (0, "b")), 2, "_")
        text = format_configuration(InstantaneousDescription(7, "q", tape))
        self.assertIn("Paso 7", text)
        self.assertIn("Estado: q", text)
        self.assertIn("'a' '_' 'b' '_' '_'", text)
        self.assertEqual(tape_text(tape), "a_b")
        lines = text.splitlines()
        self.assertEqual(lines[3].index("^"), lines[2].rindex("'"))

    def test_space_symbol_is_visible(self):
        text = format_configuration(InstantaneousDescription(0, "q", TapeSnapshot(((0, " "),), 0, "B")))
        self.assertIn("' '", text)

    def test_all_statuses_and_initial_final_ids(self):
        history = tuple(InstantaneousDescription(i, f"q{i}", TapeSnapshot((), 0, "B")) for i in range(3))
        for status, label in ((SimulationStatus.ACCEPTED, "ACEPTADA"),
                              (SimulationStatus.REJECTED, "RECHAZADA"),
                              (SimulationStatus.STEP_LIMIT, "INTERRUMPIDA POR LÍMITE DE PASOS")):
            with self.subTest(status=status):
                text = format_result(SimulationResult("", status, history))
                for i in range(3):
                    self.assertEqual(text.count(f"Paso {i} |"), 1)
                self.assertIn(f"Resultado: {label}", text)
                self.assertIn("Cinta final: ''", text)
