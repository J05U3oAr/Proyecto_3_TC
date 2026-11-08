"""Verifica los contratos que consumirán el motor y la presentación."""

import unittest
from dataclasses import FrozenInstanceError

from src.models import (
    InstantaneousDescription,
    Move,
    SimulationResult,
    SimulationStatus,
    TapeSnapshot,
    Transition,
    TuringMachine,
)


class ModelTests(unittest.TestCase):
    def test_machine_owns_an_immutable_copy_of_transitions(self):
        rule = Transition("q0", "a", "a", Move.RIGHT, "qf")
        original = {("q0", "a"): rule}
        machine = TuringMachine(
            states=frozenset({"q0", "qf"}),
            input_alphabet=frozenset({"a"}),
            tape_alphabet=frozenset({"a", "B"}),
            initial_state="q0",
            accept_states=frozenset({"qf"}),
            transitions=original,
        )
        original.clear()
        self.assertEqual(machine.transitions[("q0", "a")], rule)
        with self.assertRaises(TypeError):
            machine.transitions[("q0", "a")] = rule

    def test_instantaneous_description_is_immutable(self):
        configuration = InstantaneousDescription(0, "q0", TapeSnapshot((), 0, "B"))
        with self.assertRaises(FrozenInstanceError):
            configuration.state = "qf"

    def test_result_requires_an_initial_configuration(self):
        with self.assertRaisesRegex(ValueError, "configuración inicial"):
            SimulationResult("", SimulationStatus.REJECTED, ())

    def test_result_exposes_last_configuration(self):
        initial = InstantaneousDescription(0, "q0", TapeSnapshot((), 0, "B"))
        final = InstantaneousDescription(1, "qf", TapeSnapshot((), 1, "B"))
        result = SimulationResult("", SimulationStatus.ACCEPTED, (initial, final))
        self.assertIs(result.final_configuration, final)


if __name__ == "__main__":
    unittest.main()
