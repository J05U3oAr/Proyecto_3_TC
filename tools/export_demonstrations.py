"""Exporta las ocho ejecuciones completas y valida sus resultados esperados."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.formatter import format_result, tape_text
from src.models import SimulationStatus
from src.simulator import simulate
from src.yaml_loader import load_program


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/demostraciones")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    expected = {
        "reconocedora": [("aabbcc", SimulationStatus.ACCEPTED, None),
                         ("aaabbbccc", SimulationStatus.ACCEPTED, None),
                         ("aabbccc", SimulationStatus.REJECTED, None),
                         ("aabcbc", SimulationStatus.REJECTED, None)],
        "multiplicadora": [("10#11", SimulationStatus.ACCEPTED, "110"),
                           ("11#11", SimulationStatus.ACCEPTED, "1001"),
                           ("101#11", SimulationStatus.ACCEPTED, "1111"),
                           ("101#101", SimulationStatus.ACCEPTED, "11001")],
    }
    summary = []
    for name, cases in expected.items():
        program = load_program(ROOT / "examples" / f"{name}.yaml")
        if program.inputs != tuple(value for value, _, _ in cases):
            raise RuntimeError(f"Las entradas de {name} no coinciden con las demostraciones.")
        for index, (value, status, product) in enumerate(cases, 1):
            result = simulate(program.machine, value)
            content = tape_text(result.final_configuration.tape)
            if result.status != status or (product is not None and content != product):
                raise RuntimeError(f"Resultado inesperado para {name}: {value}")
            filename = f"{name}-{index}.txt"
            (args.output / filename).write_text(format_result(result) + "\n", encoding="utf-8")
            summary.append(dict(machine=name, input=value, status=result.status.value,
                                steps=result.final_configuration.step, final_tape=content,
                                trace=filename))
    (args.output / "resumen.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Ocho demostraciones verificadas en: {args.output.resolve()}")


if __name__ == "__main__":
    main()
