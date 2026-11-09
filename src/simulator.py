"""Ejecución general de máquinas deterministas de una cinta."""

from src.models import (
    InstantaneousDescription,
    SimulationResult,
    SimulationStatus,
    TuringMachine,
)
from src.tape import Tape


def simulate(
    machine: TuringMachine,
    input_string: str,
    *,
    max_steps: int = 10_000,
) -> SimulationResult:
    """Ejecuta ``input_string`` y conserva una configuración por transición."""
    if not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps < 0:
        raise ValueError("max_steps debe ser un entero no negativo.")
    if not isinstance(input_string, str):
        raise TypeError("La entrada debe ser una cadena.")
    invalid = set(input_string) - machine.input_alphabet
    if invalid:
        raise ValueError(
            "La entrada contiene símbolos fuera del alfabeto: "
            + ", ".join(repr(symbol) for symbol in sorted(invalid))
        )

    tape = Tape(input_string, blank=machine.blank)
    state = machine.initial_state
    step = 0
    history = [InstantaneousDescription(step, state, tape.snapshot())]

    while True:
        if state in machine.accept_states:
            status = SimulationStatus.ACCEPTED
            break
        transition = machine.transitions.get((state, tape.read()))
        if transition is None:
            status = SimulationStatus.REJECTED
            break
        if step >= max_steps:
            status = SimulationStatus.STEP_LIMIT
            break
        tape.write(transition.write)
        tape.move(transition.move)
        state = transition.next_state
        step += 1
        history.append(InstantaneousDescription(step, state, tape.snapshot()))

    return SimulationResult(input_string, status, tuple(history))
