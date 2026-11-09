"""Casos principales y límites de a^n b^n c^n."""

from pathlib import Path
import unittest

from src.models import SimulationStatus
from src.simulator import simulate
from src.yaml_loader import load_program


PROGRAM = load_program(Path(__file__).resolve().parents[1] / "examples" / "reconocedora.yaml")


class RecognizerTests(unittest.TestCase):
    def test_demonstration_cases(self):
        for value, expected in (("aabbcc", SimulationStatus.ACCEPTED),
                                ("aaabbbccc", SimulationStatus.ACCEPTED),
                                ("aabbccc", SimulationStatus.REJECTED),
                                ("aabcbc", SimulationStatus.REJECTED)):
            with self.subTest(value=value):
                self.assertEqual(simulate(PROGRAM.machine, value).status, expected)

    def test_empty_missing_blocks_and_wrong_order_reject(self):
        for value in ("", "aabcc", "acb", "baaccc"):
            with self.subTest(value=value):
                self.assertEqual(simulate(PROGRAM.machine, value).status, SimulationStatus.REJECTED)

    def test_single_symbol_per_block_is_minimum_accepted(self):
        self.assertEqual(simulate(PROGRAM.machine, "abc").status, SimulationStatus.ACCEPTED)


if __name__ == "__main__":
    unittest.main()
