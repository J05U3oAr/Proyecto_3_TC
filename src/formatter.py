"""Presentación del historial sin modificar los snapshots del motor."""

from src.models import InstantaneousDescription, SimulationResult, SimulationStatus, TapeSnapshot


def tape_text(tape: TapeSnapshot) -> str:
    """Contenido entre la primera y última celda no blanca, incluidos huecos."""
    cells = dict(tape.cells)
    if not cells:
        return ""
    return "".join(cells.get(i, tape.blank) for i in range(min(cells), max(cells) + 1))


def format_configuration(configuration: InstantaneousDescription) -> str:
    tape = configuration.tape
    cells = dict(tape.cells)
    first = min((*cells, tape.head))
    last = max((*cells, tape.head))
    positions = range(first, last + 1)
    # repr evita que símbolos como espacio o tabulador oculten el cabezal.
    tokens = [repr(cells.get(i, tape.blank)) for i in positions]
    width = max(len(str(first)), len(str(last)), *(len(token) for token in tokens))
    indices = " ".join(str(i).rjust(width) for i in positions)
    symbols = " ".join(token.rjust(width) for token in tokens)
    pointer = " " * ((tape.head - first) * (width + 1) + width - 1) + "^"
    return (f"Paso {configuration.step} | Estado: {configuration.state} | Cabezal: {tape.head}\n"
            f"Índice: {indices}\nCinta:  {symbols}\n        {pointer}")


def format_result(result: SimulationResult) -> str:
    labels = {
        SimulationStatus.ACCEPTED: "ACEPTADA",
        SimulationStatus.REJECTED: "RECHAZADA",
        SimulationStatus.STEP_LIMIT: "INTERRUMPIDA POR LÍMITE DE PASOS",
    }
    history = "\n\n".join(format_configuration(item) for item in result.history)
    return (f"Entrada: {result.input_string!r}\n{history}\n\n"
            f"Resultado: {labels[result.status]}\n"
            f"Transiciones: {result.final_configuration.step}\n"
            f"Cinta final: {tape_text(result.final_configuration.tape)!r}")
