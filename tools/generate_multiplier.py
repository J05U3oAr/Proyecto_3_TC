"""Regenera reglas explícitas; NO se usa al ejecutar una multiplicación.

No calcula productos: expande familias finitas de transiciones de una cinta.
"""

import json
from pathlib import Path


def build_transitions():
    rules = {}

    def rule(state, read, write, move, next_state):
        assert (state, read) not in rules, (state, read)
        rules[state, read] = {"state": state, "read": read, "write": write,
                              "move": move, "next": next_state}

    def scan(state, symbols, move, target=None):
        for symbol in symbols:
            rule(state, symbol, symbol, move, target or state)

    # Validación completa antes de modificar operandos.
    scan("start", "01", "L", "sentinel")
    rule("sentinel", "B", "^", "R", "validate_a")
    scan("validate_a", "01", "R")
    rule("validate_a", "#", "#", "R", "first_b")
    scan("first_b", "01", "R", "validate_b")
    scan("validate_b", "01", "R")
    rule("validate_b", "B", "$", "R", "init_acc")
    rule("init_acc", "B", "0", "L", "at_separator")
    rule("at_separator", "$", "$", "L", "decrement")
    # Contador binario B: restar uno, o detectar que estaba en cero.
    rule("decrement", "0", "1", "L", "decrement")
    rule("decrement", "1", "0", "L", "find_a")
    rule("decrement", "#", "#", "R", "finish_seek")
    scan("find_a", "01", "L")
    rule("find_a", "#", "#", "L", "pick_0")
    # Sumar A al acumulador (almacenado con el bit menos significativo primero).
    for carry in (0, 1):
        pick = f"pick_{carry}"
        scan(pick, "xy", "L")
        for bit, mark in ((0, "x"), (1, "y")):
            go = f"go_{bit}_{carry}"
            add = f"add_{bit}_{carry}"
            rule(pick, str(bit), mark, "R", go)
            scan(go, "01xy#", "R")
            rule(go, "$", "$", "R", add)
            scan(add, "uv", "R")
            for symbol in "01B":
                total = bit + carry + (1 if symbol == "1" else 0)
                rule(add, symbol, "v" if total % 2 else "u", "L", f"return_{total // 2}")
        back = f"return_{carry}"
        scan(back, "01uv$", "L")
        rule(back, "#", "#", "L", pick)
        rule(pick, "^", "^", "R", f"finish_{carry}")
        scan(f"finish_{carry}", "xy01#", "R")
        rule(f"finish_{carry}", "$", "$", "R", f"carry_{carry}")
        scan(f"carry_{carry}", "uv", "R")
    for symbol in "01B":
        rule("carry_0", symbol, symbol, "L", "restore_acc")
    rule("carry_1", "1", "0", "R", "carry_1")
    for symbol in "0B":
        rule("carry_1", symbol, "1", "L", "restore_acc")
    scan("restore_acc", "01", "L")
    rule("restore_acc", "u", "0", "L", "restore_acc")
    rule("restore_acc", "v", "1", "L", "restore_acc")
    rule("restore_acc", "$", "$", "L", "restore_a")
    scan("restore_a", "01#", "L")
    rule("restore_a", "x", "0", "L", "restore_a")
    rule("restore_a", "y", "1", "L", "restore_a")
    rule("restore_a", "^", "^", "R", "next_round")
    scan("next_round", "01#", "R")
    rule("next_round", "$", "$", "L", "decrement")
    # Revertir el acumulador: copiar de derecha a izquierda a una zona tras @.
    scan("finish_seek", "01$", "R")
    rule("finish_seek", "B", "@", "L", "reverse_pick")
    scan("reverse_pick", "xy", "L")
    for bit, mark in (("0", "x"), ("1", "y")):
        rule("reverse_pick", bit, mark, "R", f"reverse_seek_{bit}")
        scan(f"reverse_seek_{bit}", "xy01", "R")
        rule(f"reverse_seek_{bit}", "@", "@", "R", f"append_{bit}")
        scan(f"append_{bit}", "01", "R")
        rule(f"append_{bit}", "B", bit, "L", "reverse_back")
    scan("reverse_back", "01", "L")
    rule("reverse_back", "@", "@", "L", "reverse_pick")
    rule("reverse_pick", "$", "$", "L", "erase_left")
    for symbol in "01#":
        rule("erase_left", symbol, "B", "L", "erase_left")
    rule("erase_left", "^", "B", "R", "erase_right")
    for symbol in "B$xy":
        rule("erase_right", symbol, "B", "R", "erase_right")
    rule("erase_right", "@", "B", "R", "trim")
    rule("trim", "0", "B", "R", "trim")
    rule("trim", "1", "1", "S", "accept")
    rule("trim", "B", "B", "L", "zero")
    rule("zero", "B", "0", "S", "accept")
    return list(rules.values())


def main():
    rules = build_transitions()
    states = sorted({r[key] for r in rules for key in ("state", "next")})
    fields = dict(states=states, input_alphabet=list("01#"),
                  tape_alphabet=list("01#B^$xyuv@"), initial_state="start",
                  accept_states=["accept"], blank="B")
    lines = ["# Generado por tools/generate_multiplier.py; reglas de UNA cinta.", "mt:"]
    lines += [f"  {key}: {json.dumps(value)}" for key, value in fields.items()]
    lines += ["  transitions:"]
    lines += ["    - " + json.dumps(rule) for rule in rules]
    lines += ['inputs: ["10#11", "11#11", "101#11", "101#101"]']
    path = Path(__file__).resolve().parents[1] / "examples" / "multiplicadora.yaml"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
