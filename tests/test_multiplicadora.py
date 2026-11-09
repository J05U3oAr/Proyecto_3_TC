"""Productos de referencia independientes; la MT solo ejecuta transiciones."""

from itertools import product
from pathlib import Path
import unittest

from src.formatter import tape_text
from src.models import SimulationStatus
from src.simulator import simulate
from src.yaml_loader import load_program


PROGRAM = load_program(Path(__file__).resolve().parents[1] / "examples/multiplicadora.yaml")


class MultiplierTests(unittest.TestCase):
    def assert_product(self, left, right):
        result = simulate(PROGRAM.machine, f"{left}#{right}", max_steps=100_000)
        self.assertEqual(result.status, SimulationStatus.ACCEPTED)
        expected = format(int(left, 2) * int(right, 2), "b")
        self.assertEqual(tape_text(result.final_configuration.tape), expected)
        cells = result.final_configuration.tape.cells
        self.assertEqual(len(cells), len(expected))
        self.assertTrue(all(symbol in "01" for _, symbol in cells))
        self.assertEqual(result.history[0].tape.head, 0)
        self.assertEqual(len(result.history), result.final_configuration.step + 1)
        return result

    def test_demonstrations(self):
        for value in PROGRAM.inputs:
            with self.subTest(value=value):
                self.assert_product(*value.split("#"))

    def test_all_small_operands(self):
        for left in range(16):
            for right in range(16):
                with self.subTest(left=left, right=right):
                    self.assert_product(format(left, "b"), format(right, "b"))

    def test_zero_leading_zeros_and_carries(self):
        for left, right in (("000", "000"), ("000", "111"), ("111", "000"),
                            ("00101", "00011"), ("1", "1"), ("11111", "11111"),
                            ("10000", "10"), ("11111111", "1")):
            with self.subTest(left=left, right=right):
                self.assert_product(left, right)

    def test_all_short_malformed_inputs_reject(self):
        for length in range(6):
            for symbols in product("01#", repeat=length):
                value = "".join(symbols)
                parts = value.split("#")
                if len(parts) == 2 and all(parts):
                    continue
                with self.subTest(value=value):
                    self.assertEqual(simulate(PROGRAM.machine, value).status, SimulationStatus.REJECTED)

    def test_budget_and_reexecution(self):
        interrupted = simulate(PROGRAM.machine, "101#101", max_steps=10)
        self.assertEqual(interrupted.status, SimulationStatus.STEP_LIMIT)
        self.assertEqual(len(interrupted.history), 11)
        self.assert_product("101", "101")

    def test_every_recorded_step_matches_the_yaml_rule(self):
        result = self.assert_product("11", "11")
        for before, after in zip(result.history, result.history[1:]):
            cells = dict(before.tape.cells)
            symbol = cells.get(before.tape.head, before.tape.blank)
            rule = PROGRAM.machine.transitions[before.state, symbol]
            if rule.write == before.tape.blank:
                cells.pop(before.tape.head, None)
            else:
                cells[before.tape.head] = rule.write
            self.assertEqual(after.tape.cells, tuple(sorted(cells.items())))
            self.assertEqual(after.state, rule.next_state)
            self.assertEqual(after.tape.head, before.tape.head + {"L": -1, "R": 1, "S": 0}[rule.move])
