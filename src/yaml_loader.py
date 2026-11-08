"""Carga segura y validación de configuraciones deterministas de una cinta."""

from pathlib import Path
from typing import Any

import yaml

from src.models import MachineProgram, Move, Transition, TuringMachine


class ConfigurationError(ValueError):
    """Un archivo no se pudo leer o no describe una configuración válida."""


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader que no descarta silenciosamente campos repetidos."""


def _construct_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        line = key_node.start_mark.line + 1
        if not isinstance(key, str):
            raise ConfigurationError(
                f"Línea {line}: las claves del YAML deben ser texto."
            )
        if key in result:
            raise ConfigurationError(f"Línea {line}: campo duplicado '{key}'.")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def _mapping(
    value: Any, path: str, required: set[str], optional: set[str] | None = None
) -> dict:
    if not isinstance(value, dict):
        raise ConfigurationError(f"{path}: se esperaba un objeto YAML.")
    missing = required - value.keys()
    if missing:
        raise ConfigurationError(
            f"{path}: faltan campos obligatorios: {', '.join(sorted(missing))}."
        )
    unknown = value.keys() - required - (optional or set())
    if unknown:
        raise ConfigurationError(
            f"{path}: campos desconocidos: {', '.join(sorted(unknown))}."
        )
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{path}: se esperaba texto no vacío.")
    return value


def _symbol(value: Any, path: str) -> str:
    if not isinstance(value, str) or len(value) != 1:
        raise ConfigurationError(
            f"{path}: se esperaba un símbolo de un carácter; usa comillas "
            "para números y valores booleanos de YAML."
        )
    return value


def _strings(
    value: Any, path: str, *, symbols: bool = False, nonempty: bool = False
) -> frozenset[str]:
    if not isinstance(value, list) or (nonempty and not value):
        qualifier = " no vacía" if nonempty else ""
        raise ConfigurationError(f"{path}: se esperaba una lista{qualifier}.")
    validate = _symbol if symbols else _text
    result = set()
    for index, item in enumerate(value):
        item = validate(item, f"{path}[{index}]")
        if item in result:
            raise ConfigurationError(f"{path}: elemento duplicado '{item}'.")
        result.add(item)
    return frozenset(result)


def _transition_symbol(value: Any, path: str) -> str:
    if isinstance(value, list):
        if len(value) != 1:
            raise ConfigurationError(
                f"{path}: una MT de una cinta lee o escribe un solo símbolo; "
                "usa un escalar o una lista de un elemento. Las listas de "
                "varios símbolos del ejemplo del enunciado son ambiguas."
            )
        value = value[0]
    return _symbol(value, path)


def parse_program(text: str) -> MachineProgram:
    """Convierte texto YAML en modelos validados; no ejecuta la máquina."""
    if not isinstance(text, str):
        raise ConfigurationError("La configuración YAML debe recibirse como texto.")
    try:
        raw = yaml.load(text, Loader=_UniqueKeyLoader)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        location = f" en línea {mark.line + 1}" if mark else ""
        problem = getattr(exc, "problem", None) or str(exc)
        raise ConfigurationError(f"YAML inválido{location}: {problem}") from exc

    root = _mapping(raw, "raíz", {"mt", "inputs"})
    data = _mapping(
        root["mt"],
        "mt",
        {
            "states", "input_alphabet", "tape_alphabet", "initial_state",
            "accept_states", "transitions",
        },
        {"blank"},
    )
    states = _strings(data["states"], "mt.states", nonempty=True)
    input_alphabet = _strings(
        data["input_alphabet"], "mt.input_alphabet", symbols=True
    )
    tape_alphabet = _strings(
        data["tape_alphabet"], "mt.tape_alphabet", symbols=True, nonempty=True
    )
    blank = _symbol(data.get("blank", "B"), "mt.blank")
    if not input_alphabet <= tape_alphabet:
        raise ConfigurationError(
            "mt.input_alphabet: debe ser subconjunto de mt.tape_alphabet."
        )
    if blank not in tape_alphabet:
        raise ConfigurationError("mt.blank: debe pertenecer a mt.tape_alphabet.")
    if blank in input_alphabet:
        raise ConfigurationError("mt.blank: no puede pertenecer a mt.input_alphabet.")

    initial_state = _text(data["initial_state"], "mt.initial_state")
    if initial_state not in states:
        raise ConfigurationError("mt.initial_state: el estado no existe en mt.states.")
    accept_states = _strings(data["accept_states"], "mt.accept_states")
    if not accept_states <= states:
        raise ConfigurationError("mt.accept_states: contiene estados no declarados.")

    raw_transitions = data["transitions"]
    if not isinstance(raw_transitions, list):
        raise ConfigurationError("mt.transitions: se esperaba una lista.")
    transitions = {}
    for index, value in enumerate(raw_transitions):
        path = f"mt.transitions[{index}]"
        rule = _mapping(value, path, {"state", "read", "write", "move", "next"})
        state = _text(rule["state"], f"{path}.state")
        next_state = _text(rule["next"], f"{path}.next")
        if state not in states or next_state not in states:
            raise ConfigurationError(f"{path}: state y next deben existir en mt.states.")
        read = _transition_symbol(rule["read"], f"{path}.read")
        write = _transition_symbol(rule["write"], f"{path}.write")
        if read not in tape_alphabet or write not in tape_alphabet:
            raise ConfigurationError(
                f"{path}: read y write deben pertenecer a mt.tape_alphabet."
            )
        direction = _text(rule["move"], f"{path}.move")
        try:
            move = Move(direction)
        except ValueError as exc:
            raise ConfigurationError(f"{path}.move: usa L, R o S.") from exc
        key = (state, read)
        if key in transitions:
            raise ConfigurationError(
                f"{path}: transición duplicada para ({state}, {read}); "
                "la máquina debe ser determinista."
            )
        transitions[key] = Transition(state, read, write, move, next_state)

    raw_inputs = root["inputs"]
    if not isinstance(raw_inputs, list) or not raw_inputs:
        raise ConfigurationError("inputs: se esperaba una lista no vacía de cadenas.")
    inputs = []
    for index, value in enumerate(raw_inputs):
        if not isinstance(value, str):
            raise ConfigurationError(f"inputs[{index}]: usa una cadena entre comillas.")
        invalid = set(value) - input_alphabet
        if invalid:
            raise ConfigurationError(
                f"inputs[{index}]: símbolos fuera del alfabeto de entrada: "
                f"{', '.join(repr(symbol) for symbol in sorted(invalid))}."
            )
        inputs.append(value)

    return MachineProgram(
        machine=TuringMachine(
            states=states,
            input_alphabet=input_alphabet,
            tape_alphabet=tape_alphabet,
            initial_state=initial_state,
            accept_states=accept_states,
            transitions=transitions,
            blank=blank,
        ),
        inputs=tuple(inputs),
    )


def load_program(path: str | Path) -> MachineProgram:
    """Lee un YAML UTF-8 (con o sin BOM) y devuelve su configuración validada."""
    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise ConfigurationError(f"No se pudo leer '{file_path}': {exc}") from exc
    return parse_program(text)
