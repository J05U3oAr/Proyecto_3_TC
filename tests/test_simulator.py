"""Pruebas de terminación e independencia del motor."""

import unittest

from src.models import Move, SimulationStatus, Transition, TuringMachine
from src.simulator import simulate


def machine(transitions=(), *, accept=("qf",), alphabet=("a",)):
    return TuringMachine(
        states=frozenset({"q0", "qf"}), input_alphabet=frozenset(alphabet),
        tape_alphabet=frozenset(set(alphabet) | {"B", "X"}), initial_state="q0",
        accept_states=frozenset(accept),
        transitions={(rule.state, rule.read): rule for rule in transitions},
    )


class SimulatorTests(unittest.TestCase):
    def test_accepts_initial_state_and_empty_input(self):
        result = simulate(machine(accept=("q0",), alphabet=()), "")
        self.assertEqual(result.status, SimulationStatus.ACCEPTED)
        self.assertEqual([item.step for item in result.history], [0])

    def test_missing_rule_rejects(self):
        result = simulate(machine(), "a")
        self.assertEqual(result.status, SimulationStatus.REJECTED)
        self.assertEqual(len(result.history), 1)

    def test_accepts_exactly_at_step_limit(self):
        rule = Transition("q0", "a", "X", Move.RIGHT, "qf")
        result = simulate(machine((rule,)), "a", max_steps=1)
        self.assertEqual(result.status, SimulationStatus.ACCEPTED)
        self.assertEqual([item.step for item in result.history], [0, 1])

    def test_step_limit_only_when_another_transition_is_needed(self):
        rule = Transition("q0", "a", "X", Move.STAY, "q0")
        result = simulate(machine((rule,)), "a", max_steps=0)
        self.assertEqual(result.status, SimulationStatus.STEP_LIMIT)

    def test_snapshots_are_independent_across_steps_and_runs(self):
        rules = (Transition("q0", "a", "X", Move.RIGHT, "q0"),)
        result = simulate(machine(rules), "aa")
        other = simulate(machine(rules), "aa")
        self.assertEqual(len(result.history), 3)
        self.assertEqual(result.history[0].tape.cells, ((0, "a"), (1, "a")))
        self.assertNotEqual(result.history[1].tape.cells, result.history[2].tape.cells)
        self.assertEqual(result.history, other.history)

    def test_validates_step_budget_and_input_alphabet(self):
        for limit in (-1, True, 1.5):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                simulate(machine(), "a", max_steps=limit)
        with self.assertRaisesRegex(ValueError, "alfabeto"):
            simulate(machine(), "b")


if __name__ == "__main__":
    unittest.main()
