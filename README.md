# Proyecto 3: máquinas de Turing

Proyecto de Teoría de la Computación. El objetivo es simular máquinas de Turing
deterministas de **una cinta**, definidas mediante archivos YAML.

## Instalación

Requisitos: Python 3.11 o posterior y Git. Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

En Linux o macOS, sustituir `.venv\Scripts\python.exe` por `.venv/bin/python`.
La activación del entorno es opcional si se utiliza directamente su ejecutable.

## Distribución del trabajo

Cada tarea tiene un único responsable. La base se implementa primero; luego
Alejandro y Sebas trabajan sobre sus contratos.

| Responsable | Alcance |
| --- | --- |
| J05U3oAr | Estructura, modelos y contratos, formato YAML, parser y validaciones, cinta y pruebas de la base. |
| Alejandro | Motor e historial de ejecución, terminación, reconocedora de `a^n b^n c^n`, pruebas del motor y de la reconocedora, integración final. |
| Sebas | Consola y visualización, multiplicadora binaria, sus pruebas, README final y video de entrega. |

La reconocedora y la multiplicadora deberán ejecutar transiciones del YAML sobre
la misma implementación de cinta. El cálculo de sus resultados no se sustituye
por operaciones directas de Python.

## Estado

Las tareas 1–5 de J05U3oAr están implementadas: estructura, modelos y contratos,
formato YAML, parser con validaciones y cinta extendible con pruebas.

**Pendiente de Alejandro:** motor, terminación, reconocedora e integración final.
**Pendiente de Sebas:** consola, visualización, multiplicadora, documentación final
y video. La base aún no ejecuta simulaciones completas ni tiene interfaz de consola.

Los contratos y el detalle del trabajo pendiente están en
[docs/arquitectura.md](docs/arquitectura.md).

El [formato YAML](docs/formato_yaml.md) documenta campos, validaciones y la
decisión sobre las listas ambiguas del ejemplo del enunciado. El archivo
[examples/base.yaml](examples/base.yaml) es una configuración mínima de prueba,
no una de las máquinas evaluadas.

## Comprobar la base

Desde la raíz, con las dependencias instaladas:

```powershell
.venv\Scripts\python.exe -c "from src.yaml_loader import load_program; p = load_program('examples/base.yaml'); print('Entradas:', p.inputs); print('Transiciones:', len(p.machine.transitions))"
```

Debe mostrar las entradas `('', 'a', 'aaa')` y dos transiciones. La configuración
se carga y valida; no se ejecuta la máquina.

Ejemplo de uso de la API de cinta en Python:

```python
from src.tape import Tape
from src.yaml_loader import load_program

program = load_program("examples/base.yaml")
tape = Tape(program.inputs[1], blank=program.machine.blank)
initial = tape.snapshot()
print(tape.read())  # a
tape.move("L")
print(tape.head, tape.read())  # -1 B
print(initial.head)  # 0: el snapshot anterior se conserva
```

## Archivos implementados

```text
src/
  __init__.py
  models.py
  yaml_loader.py
  tape.py
docs/
  arquitectura.md
  formato_yaml.md
examples/
  base.yaml
tests/
  test_models.py
  test_yaml_loader.py
  test_tape.py
```

Alejandro y Sebas crearán sus módulos y archivos YAML según los contratos de
arquitectura. Cada integrante debe usar su propia identidad de Git y conservar
sus commits al integrar las ramas.

## Pruebas

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas usan `unittest`, incluido en Python; no requieren dependencias extra.
Cubren carga de archivos, sintaxis y validación semántica, determinismo,
inmutabilidad del historial, movimientos, escritura y blancos, posiciones
negativas y aislamiento entre cintas.
