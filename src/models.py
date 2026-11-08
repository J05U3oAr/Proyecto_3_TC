"""Contratos compartidos; este módulo no ejecuta transiciones."""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class Move(str, Enum):
    """Desplazamiento de un único cabezal."""

    LEFT = "L"
    RIGHT = "R"
    STAY = "S"


@dataclass(frozen=True, slots=True)
class Transition:
    state: str
    read: str
    write: str
    move: Move
    next_state: str


@dataclass(frozen=True, slots=True)
class TuringMachine:
    states: frozenset[str]
    input_alphabet: frozenset[str]
    tape_alphabet: frozenset[str]
    initial_state: str
    accept_states: frozenset[str]
    transitions: Mapping[tuple[str, str], Transition]
    blank: str = "B"

    def __post_init__(self) -> None:
        # Copiar antes de exponer: el diccionario original no puede mutar la MT.
        object.__setattr__(
            self, "transitions", MappingProxyType(dict(self.transitions))
        )


@dataclass(frozen=True, slots=True)
class MachineProgram:
    """Una configuración de MT y las entradas independientes que debe procesar."""

    machine: TuringMachine
    inputs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TapeSnapshot:
    """Celdas no blancas ordenadas por posición, independientes de la cinta viva."""

    cells: tuple[tuple[int, str], ...]
    head: int
    blank: str


@dataclass(frozen=True, slots=True)
class InstantaneousDescription:
    step: int
    state: str
    tape: TapeSnapshot


class SimulationStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    STEP_LIMIT = "step_limit"


@dataclass(frozen=True, slots=True)
class SimulationResult:
    """Contrato para el futuro motor; el historial incluye la ID inicial."""

    input_string: str
    status: SimulationStatus
    history: tuple[InstantaneousDescription, ...]

    def __post_init__(self) -> None:
        if not self.history:
            raise ValueError("El historial debe incluir la configuración inicial.")

    @property
    def final_configuration(self) -> InstantaneousDescription:
        return self.history[-1]
