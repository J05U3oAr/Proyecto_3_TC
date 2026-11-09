"""Consola: python -m src.main archivo.yaml --max-steps 10000."""

import argparse
import sys

from src.formatter import format_result
from src.models import SimulationStatus
from src.simulator import simulate
from src.yaml_loader import ConfigurationError, load_program


def nonnegative_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("debe ser un entero no negativo") from exc
    if number < 0:
        raise argparse.ArgumentTypeError("debe ser un entero no negativo")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Simulador general de MT deterministas de una cinta")
    parser.add_argument("yaml", help="archivo YAML de la máquina y sus entradas")
    parser.add_argument("--max-steps", type=nonnegative_integer, default=10_000,
                        help="máximo de transiciones por entrada (por defecto: 10000)")
    args = parser.parse_args(argv)
    try:
        program = load_program(args.yaml)
    except ConfigurationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    interrupted = False
    for index, value in enumerate(program.inputs, start=1):
        result = simulate(program.machine, value, max_steps=args.max_steps)
        print(f"=== Ejecución {index}/{len(program.inputs)} ===")
        print(format_result(result))
        print()
        interrupted |= result.status == SimulationStatus.STEP_LIMIT
    return 1 if interrupted else 0


if __name__ == "__main__":
    raise SystemExit(main())
