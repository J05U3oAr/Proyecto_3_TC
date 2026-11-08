"""Pruebas del límite de entrada: configuraciones válidas y errores útiles."""

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import yaml

from src.models import Move
from src.yaml_loader import ConfigurationError, load_program, parse_program


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "base.yaml"


def valid_data():
    return {
        "mt": {
            "states": ["q0", "qf"],
            "input_alphabet": ["a"],
            "tape_alphabet": ["a", "B"],
            "initial_state": "q0",
            "accept_states": ["qf"],
            "transitions": [
                {"state": "q0", "read": "a", "write": "a", "move": "R", "next": "qf"}
            ],
        },
        "inputs": ["", "aaa", "a", "a"],
    }


def parse_data(data):
    return parse_program(yaml.safe_dump(data, allow_unicode=True))


class YamlLoaderTests(unittest.TestCase):
    def test_loads_example_without_executing_it(self):
        program = load_program(EXAMPLE)
        self.assertEqual(program.machine.initial_state, "q0")
        self.assertEqual(program.inputs, ("", "a", "aaa"))
        self.assertEqual(program.machine.transitions[("q0", "B")].move, Move.STAY)

    def test_defaults_blank_and_preserves_input_order_and_duplicates(self):
        program = parse_data(valid_data())
        self.assertEqual(program.machine.blank, "B")
        self.assertEqual(program.inputs, ("", "aaa", "a", "a"))

    def test_supports_custom_blank_singleton_lists_and_all_moves(self):
        for direction in Move:
            with self.subTest(direction=direction):
                data = valid_data()
                data["mt"]["blank"] = "_"
                data["mt"]["tape_alphabet"] = ["a", "_"]
                rule = data["mt"]["transitions"][0]
                rule.update(read=["a"], write=["_"], move=direction.value)
                program = parse_data(data)
                transition = program.machine.transitions[("q0", "a")]
                self.assertEqual(transition.write, "_")
                self.assertEqual(transition.move, direction)

    def test_allows_empty_transition_and_acceptance_sets(self):
        data = valid_data()
        data["mt"].update(transitions=[], accept_states=[])
        program = parse_data(data)
        self.assertEqual(len(program.machine.transitions), 0)
        self.assertEqual(program.machine.accept_states, frozenset())

    def test_allows_empty_alphabet_for_empty_input(self):
        data = valid_data()
        data["mt"].update(input_alphabet=[], tape_alphabet=["B"], transitions=[])
        data["inputs"] = [""]
        self.assertEqual(parse_data(data).inputs, ("",))

    def test_accepts_quoted_binary_symbols_and_separator(self):
        data = valid_data()
        data["mt"].update(
            input_alphabet=["0", "1", "#"],
            tape_alphabet=["0", "1", "#", "B"],
            transitions=[],
        )
        data["inputs"] = ["101#11"]
        self.assertEqual(parse_data(data).inputs, ("101#11",))

    def test_accepts_single_unicode_character_and_space(self):
        data = valid_data()
        data["mt"].update(
            input_alphabet=["ñ", " "], tape_alphabet=["ñ", " ", "B"], transitions=[]
        )
        data["inputs"] = ["ñ ñ"]
        self.assertEqual(parse_data(data).inputs, ("ñ ñ",))

    def test_rejects_missing_required_fields_at_every_level(self):
        template = valid_data()
        for section in ("root", "mt", "transition"):
            source = (
                template if section == "root" else template["mt"]
                if section == "mt" else template["mt"]["transitions"][0]
            )
            for key in source:
                with self.subTest(section=section, key=key):
                    data = deepcopy(template)
                    target = (
                        data if section == "root" else data["mt"]
                        if section == "mt" else data["mt"]["transitions"][0]
                    )
                    del target[key]
                    with self.assertRaisesRegex(ConfigurationError, "obligatorios"):
                        parse_data(data)

    def test_rejects_unknown_fields_at_every_level(self):
        for section in ("root", "mt", "transition"):
            with self.subTest(section=section):
                data = valid_data()
                target = (
                    data if section == "root" else data["mt"]
                    if section == "mt" else data["mt"]["transitions"][0]
                )
                target["typo"] = "value"
                with self.assertRaisesRegex(ConfigurationError, "desconocidos"):
                    parse_data(data)

    def test_rejects_duplicate_elements(self):
        for field, item in (
            ("states", "q0"), ("input_alphabet", "a"),
            ("tape_alphabet", "B"), ("accept_states", "qf"),
        ):
            with self.subTest(field=field):
                data = valid_data()
                data["mt"][field].append(item)
                with self.assertRaisesRegex(ConfigurationError, "duplicado"):
                    parse_data(data)

    def test_rejects_invalid_alphabet_relationships(self):
        for changes, message in (
            ({"input_alphabet": ["x"]}, "subconjunto"),
            ({"tape_alphabet": ["a"]}, "mt.blank"),
            ({"input_alphabet": ["a", "B"]}, "mt.blank"),
            ({"blank": "__"}, "un carácter"),
        ):
            with self.subTest(changes=changes):
                data = valid_data()
                data["mt"].update(changes)
                with self.assertRaisesRegex(ConfigurationError, message):
                    parse_data(data)

    def test_rejects_undeclared_initial_and_acceptance_states(self):
        for field, value in (("initial_state", "missing"), ("accept_states", ["missing"])):
            with self.subTest(field=field):
                data = valid_data()
                data["mt"][field] = value
                with self.assertRaisesRegex(ConfigurationError, field):
                    parse_data(data)

    def test_rejects_invalid_transition_references_and_moves(self):
        for field, value, message in (
            ("state", "missing", "state y next"),
            ("next", "missing", "state y next"),
            ("read", "x", "read y write"),
            ("write", "x", "read y write"),
            ("move", "LEFT", "L, R o S"),
        ):
            with self.subTest(field=field):
                data = valid_data()
                data["mt"]["transitions"][0][field] = value
                with self.assertRaisesRegex(ConfigurationError, message):
                    parse_data(data)

    def test_rejects_ambiguous_or_empty_read_and_write_lists(self):
        for field in ("read", "write"):
            for value in ([], ["a", "B"]):
                with self.subTest(field=field, value=value):
                    data = valid_data()
                    data["mt"]["transitions"][0][field] = value
                    with self.assertRaisesRegex(ConfigurationError, "una cinta"):
                        parse_data(data)

    def test_rejects_duplicate_transition_keys_even_with_different_results(self):
        for next_state in ("q0", "qf"):
            with self.subTest(next_state=next_state):
                data = valid_data()
                second = deepcopy(data["mt"]["transitions"][0])
                second["next"] = next_state
                data["mt"]["transitions"].append(second)
                with self.assertRaisesRegex(ConfigurationError, "determinista"):
                    parse_data(data)

    def test_rejects_wrong_container_types_and_empty_required_lists(self):
        for field, value in (
            ("states", []), ("states", "q0"), ("states", [""]),
            ("input_alphabet", "a"), ("tape_alphabet", []),
            ("accept_states", "qf"), ("transitions", {}),
            ("transitions", ["not a rule"]),
        ):
            with self.subTest(field=field, value=value):
                data = valid_data()
                data["mt"][field] = value
                with self.assertRaises(ConfigurationError):
                    parse_data(data)

    def test_rejects_non_character_symbols_and_implicit_scalar_types(self):
        for value in (0, True, None, "ab", ""):
            with self.subTest(value=value):
                data = valid_data()
                data["mt"]["input_alphabet"] = [value]
                with self.assertRaisesRegex(ConfigurationError, "un carácter"):
                    parse_data(data)

    def test_rejects_invalid_inputs(self):
        for value in ([], "a", [1], [True], [None], ["ab"]):
            with self.subTest(value=value):
                data = valid_data()
                data["inputs"] = value
                with self.assertRaisesRegex(ConfigurationError, "inputs"):
                    parse_data(data)

    def test_rejects_empty_non_mapping_malformed_and_multi_document_yaml(self):
        for text in ("", "[]", "null", "mt: [", "---\na: b\n---\nc: d"):
            with self.subTest(text=text):
                with self.assertRaises(ConfigurationError):
                    parse_program(text)

    def test_rejects_duplicate_yaml_keys_and_non_text_keys(self):
        for text in (
            "mt: {}\nmt: {}\ninputs: []",
            "mt:\n  states: [q0]\n  states: [qf]\ninputs: []",
            "0: value",
            "[a, b]: value",
        ):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ConfigurationError, "Línea"):
                    parse_program(text)

    def test_rejects_python_object_tags(self):
        with self.assertRaisesRegex(ConfigurationError, "YAML inválido"):
            parse_program("!!python/object/apply:builtins.str [123]")

    def test_requires_yaml_text(self):
        with self.assertRaisesRegex(ConfigurationError, "texto"):
            parse_program(None)

    def test_reads_utf8_with_bom_and_reports_file_errors(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "machine.yaml"
            text = yaml.safe_dump(valid_data())
            path.write_text(text, encoding="utf-8-sig")
            self.assertEqual(load_program(path).machine.blank, "B")
            path.write_bytes(b"\xff\xfe")
            with self.assertRaisesRegex(ConfigurationError, "No se pudo leer"):
                load_program(path)
            with self.assertRaisesRegex(ConfigurationError, "No se pudo leer"):
                load_program(Path(folder) / "missing.yaml")
            with self.assertRaisesRegex(ConfigurationError, "No se pudo leer"):
                load_program(folder)


if __name__ == "__main__":
    unittest.main()
