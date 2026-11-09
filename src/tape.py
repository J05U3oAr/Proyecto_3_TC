"""Cinta dispersa, extendible en ambos sentidos, con un único cabezal."""

from src.models import Move, TapeSnapshot


def _validate_symbol(symbol: str, name: str) -> None:
    if not isinstance(symbol, str):
        raise TypeError(f"{name} debe ser texto.")
    if len(symbol) != 1:
        raise ValueError(f"{name} debe tener exactamente un carácter.")


class Tape:
    """Almacena solo celdas no blancas; no interpreta reglas de la MT."""

    __slots__ = ("_cells", "_head", "_blank")

    def __init__(self, input_string: str = "", blank: str = "B") -> None:
        if not isinstance(input_string, str):
            raise TypeError("La entrada de la cinta debe ser una cadena.")
        _validate_symbol(blank, "El blanco")
        self._blank = blank
        self._head = 0
        self._cells = {
            position: symbol
            for position, symbol in enumerate(input_string)
            if symbol != blank
        }

    @property
    def head(self) -> int:
        return self._head

    @property
    def blank(self) -> str:
        return self._blank

    def read(self) -> str:
        return self._cells.get(self._head, self._blank)

    def write(self, symbol: str) -> None:
        _validate_symbol(symbol, "El símbolo")
        if symbol == self._blank:
            self._cells.pop(self._head, None)
        else:
            self._cells[self._head] = symbol

    def move(self, direction: Move | str) -> None:
        try:
            movement = Move(direction)
        except (TypeError, ValueError) as exc:
            raise ValueError("El movimiento debe ser L, R o S.") from exc
        if movement == Move.LEFT:
            self._head -= 1
        elif movement == Move.RIGHT:
            self._head += 1

    def snapshot(self) -> TapeSnapshot:
        return TapeSnapshot(
            cells=tuple(sorted(self._cells.items())),
            head=self._head,
            blank=self._blank,
        )
