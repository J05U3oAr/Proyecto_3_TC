"""Verifica límites, escritura y conservación del historial de la cinta."""

from dataclasses import FrozenInstanceError
from pathlib import Path
import unittest

from src.models import Move, TapeSnapshot
from src.tape import Tape
from src.yaml_loader import load_program


class TapeTests(unittest.TestCase):
    def test_loads_input_at_zero_and_starts_on_first_character(self):
        tape = Tape("abc")
        self.assertEqual(tape.head, 0)
        self.assertEqual(tape.read(), "a")
        tape.move("R")
        self.assertEqual(tape.read(), "b")
        tape.move(Move.RIGHT)
        self.assertEqual(tape.read(), "c")
        tape.move("R")
        self.assertEqual(tape.read(), "B")

    def test_empty_input_has_a_readable_blank_cell(self):
        tape = Tape()
        self.assertEqual(tape.read(), "B")
        self.assertEqual(tape.snapshot(), TapeSnapshot((), 0, "B"))

    def test_can_write_and_revisit_negative_and_positive_positions(self):
        tape = Tape("a")
        tape.move("L")
        tape.move("L")
        self.assertEqual(tape.read(), "B")
        tape.write("X")
        for _ in range(5):
            tape.move("R")
        self.assertEqual(tape.head, 3)
        self.assertEqual(tape.read(), "B")
        tape.write("Y")
        for _ in range(5):
            tape.move("L")
        self.assertEqual(tape.read(), "X")
        self.assertEqual(tape.snapshot().cells, ((-2, "X"), (0, "a"), (3, "Y")))

    def test_overwriting_a_symbol_does_not_move_the_head(self):
        tape = Tape("a")
        tape.write("X")
        self.assertEqual(tape.read(), "X")
        self.assertEqual(tape.head, 0)

    def test_writing_blank_erases_cell_and_preserves_other_cells(self):
        tape = Tape("ab")
        tape.write("B")
        self.assertEqual(tape.read(), "B")
        self.assertEqual(tape.snapshot().cells, ((1, "b"),))
        tape.move("L")
        tape.write("B")
        self.assertEqual(tape.snapshot().cells, ((1, "b"),))

    def test_custom_blank_and_embedded_blank_are_not_stored(self):
        tape = Tape("a_b", blank="_")
        self.assertEqual(tape.blank, "_")
        self.assertEqual(tape.snapshot().cells, ((0, "a"), (2, "b")))
        tape.move("R")
        self.assertEqual(tape.read(), "_")
        tape.move("L")
        tape.write("_")
        self.assertEqual(tape.snapshot().cells, ((2, "b"),))

    def test_stay_does_not_move_or_change_contents(self):
        tape = Tape("a")
        before = tape.snapshot()
        tape.move(Move.STAY)
        tape.move("S")
        self.assertEqual(tape.snapshot(), before)

    def test_snapshot_does_not_change_after_writing_moving_or_erasing(self):
        tape = Tape("ab")
        initial = tape.snapshot()
        tape.write("X")
        tape.move("R")
        tape.write("B")
        self.assertEqual(initial, TapeSnapshot(((0, "a"), (1, "b")), 0, "B"))
        self.assertEqual(tape.snapshot(), TapeSnapshot(((0, "X"),), 1, "B"))
        with self.assertRaises(FrozenInstanceError):
            initial.head = 5

    def test_independent_tapes_do_not_share_cells_or_head(self):
        first = Tape("a")
        second = Tape("a")
        first.write("X")
        first.move("L")
        self.assertEqual(second.read(), "a")
        self.assertEqual(second.head, 0)

    def test_invalid_movements_do_not_modify_the_tape(self):
        tape = Tape("a")
        initial = tape.snapshot()
        for value in ("LEFT", "", "r", 1, None, []):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "L, R o S"):
                    tape.move(value)
                self.assertEqual(tape.snapshot(), initial)

    def test_rejects_invalid_blanks_inputs_and_writes(self):
        for value in (None, 1, [], "", "ab"):
            with self.subTest(value=value):
                expected_error = ValueError if isinstance(value, str) else TypeError
                with self.assertRaises(expected_error):
                    Tape(blank=value)
                tape = Tape("a")
                with self.assertRaises(expected_error):
                    tape.write(value)
                self.assertEqual(tape.read(), "a")
        for value in (None, 123, ["a"]):
            with self.subTest(input=value):
                with self.assertRaises(TypeError):
                    Tape(value)

    def test_unicode_and_space_are_single_cell_symbols(self):
        tape = Tape("ñ ")
        self.assertEqual(tape.read(), "ñ")
        tape.move("R")
        self.assertEqual(tape.read(), " ")
        tape.write("λ")
        self.assertEqual(tape.snapshot().cells, ((0, "ñ"), (1, "λ")))

    def test_head_and_blank_are_read_only_public_properties(self):
        tape = Tape("a")
        with self.assertRaises(AttributeError):
            tape.head = 5
        with self.assertRaises(AttributeError):
            tape.blank = "_"

    def test_loaded_program_can_create_independent_tapes_and_find_rules(self):
        example = Path(__file__).resolve().parents[1] / "examples" / "base.yaml"
        program = load_program(example)
        tapes = [Tape(value, blank=program.machine.blank) for value in program.inputs]
        self.assertEqual([tape.read() for tape in tapes], ["B", "a", "a"])
        rule = program.machine.transitions[(program.machine.initial_state, tapes[1].read())]
        self.assertEqual(rule.next_state, "q0")
        tapes[1].write("X")
        self.assertEqual(tapes[2].read(), "a")


if __name__ == "__main__":
    unittest.main()
