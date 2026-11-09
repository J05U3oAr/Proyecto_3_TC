# Arquitectura y contratos de la base

## Responsabilidades

La base contiene datos y operaciones de cinta; el motor y la consola ya están
implementados sobre esos contratos.

| Archivo | Responsable | Función |
| --- | --- | --- |
| `src/models.py` | J05U3oAr | Contratos compartidos. |
| `src/yaml_loader.py` | J05U3oAr | Carga y validación del YAML. |
| `src/tape.py` | J05U3oAr | Cinta dispersa y cabezal. |
| `src/simulator.py` | Alejandro | Ejecución de transiciones e historial. |
| `examples/reconocedora.yaml` | Alejandro | Reconocer `a^n b^n c^n`, con `n >= 1`. |
| `src/formatter.py` | Sebas | Presentación de las descripciones instantáneas. |
| `src/main.py` | Sebas | Interfaz de consola. |
| `examples/multiplicadora.yaml` | Sebas | Multiplicación de operandos binarios. |

Ambas máquinas se ejecutan con el mismo motor. La consola llama a `simulate`
por cada entrada y el formateador presenta todos los snapshots del resultado.

## Modelos

- `Move`: `L` (izquierda), `R` (derecha), `S` (sin desplazamiento).
- `Transition(state, read, write, move, next_state)`: una regla determinista.
- `TuringMachine`: estados, alfabetos, estado inicial, estados de aceptación,
  blanco y tabla de transiciones indexada por `(estado, símbolo leído)`.
- `MachineProgram(machine, inputs)`: configuración y tupla de entradas.
- `TapeSnapshot(cells, head, blank)`: copia inmutable de la cinta; `cells` es una
  tupla de pares `(posición, símbolo)` ordenada, que omite las celdas blancas.
- `InstantaneousDescription(step, state, tape)`: un paso, su estado y snapshot.
- `SimulationResult(input_string, status, history)`: salida del motor.
  `final_configuration` devuelve la última ID. El historial no puede estar vacío.

Los modelos usan `dataclass(frozen=True)`, colecciones inmutables y una copia
protegida de la tabla de transiciones. Las reglas semánticas de la configuración
se validan en el parser; construir estos modelos directamente presupone datos
válidos y colecciones de los tipos declarados.

## API de carga y cinta

```python
from src.yaml_loader import load_program, parse_program, ConfigurationError
from src.tape import Tape

program = load_program("examples/base.yaml")
# Alternativa para texto YAML en memoria: parse_program(texto_yaml).
machine = program.machine
tape = Tape(program.inputs[0], blank=machine.blank)
symbol = tape.read()
transition = machine.transitions.get((machine.initial_state, symbol))
initial_snapshot = tape.snapshot()
```

El motor de Alejandro ejecuta la regla encontrada. `ConfigurationError` informa
errores de archivo, sintaxis o configuración con un mensaje dirigido a la persona
que edita el YAML.

`Tape` expone:

| Operación | Contrato |
| --- | --- |
| `Tape(input_string="", blank="B")` | Copia la entrada desde la posición 0; cabezal inicial en 0. |
| `head`, `blank` | Propiedades de lectura. Las posiciones pueden ser negativas. |
| `read()` | Lee la celda actual; una celda no almacenada contiene el blanco. |
| `write(symbol)` | Escribe un carácter. Escribir el blanco elimina la celda almacenada. |
| `move(direction)` | Acepta `Move` o los textos `L`, `R`, `S`. |
| `snapshot()` | Captura independiente que no cambia cuando se modifica la cinta. |

La cinta no conoce estados, alfabetos ni aceptación. El parser valida los símbolos
configurados; el motor ejecuta las reglas previamente validadas.

## Contrato implementado por el motor

API utilizada por la consola:

```python
simulate(
    machine: TuringMachine,
    input_string: str,
    *,
    max_steps: int = 10_000,
) -> SimulationResult
```

Esta función se importa de `src.simulator`. Su comportamiento es:

1. Crear una cinta nueva por entrada y comenzar en `initial_state`, paso 0.
2. Guardar la ID inicial antes de aplicar transiciones.
3. Aceptar al alcanzar un estado de `accept_states`, incluso en el paso 0.
4. En otro estado, rechazar si no existe regla para `(estado, tape.read())`.
5. Aplicar escritura, movimiento y cambio de estado; guardar una nueva ID.
6. Detenerse con `STEP_LIMIT` si se agota el máximo de transiciones aplicadas y
   todavía se requiere otra transición. No presentar ese resultado como rechazo.

El historial completo usa snapshots, nunca referencias a una misma cinta mutable.
El formateador muestra la posición del cabezal también sobre blancos e índices
negativos. El intervalo incluye el cabezal y todas las celdas no blancas; una
cinta vacía sigue mostrando al menos una celda blanca.

## Responsabilidades y seguimiento

El motor, ambas máquinas, la consola y sus pruebas están implementados. Las listas
siguientes conservan el alcance de cada responsable; la integración final del
equipo y el video se siguen en el README y `docs/entrega.md`.

### Alejandro

1. Implementar y probar el motor y sus tres estados de terminación.
2. Diseñar y documentar la reconocedora en YAML.
3. Demostrar aceptación de `aabbcc` y `aaabbbccc`, y rechazo de `aabbccc` y
   `aabcbc`. Todas tienen longitud mínima de cinco.
4. Justificar el algoritmo por marcado: tiempo cuadrático y espacio lineal para
   la estrategia prevista, en función de la longitud de entrada.
5. Integrar el programa cuando estén listas las partes de Sebas.

### Sebas

1. Implementar consola y visualización sobre los contratos compartidos.
2. Diseñar e implementar la multiplicadora de una cinta mediante transiciones.
3. Documentar formato de operandos, ceros, fases, acarreos y limpieza de la cinta.
4. Demostrar `10#11 -> 110`, `11#11 -> 1001`, `101#11 -> 1111` y
   `101#101 -> 11001`; añadir pruebas de casos límite.
5. Completar el README final y grabar las ocho demostraciones y la explicación
   de arquitectura; publicar el video en YouTube como no listado y añadir el enlace.

El YAML de la base solo prueba la infraestructura. No sustituye ninguna de las
máquinas evaluadas y no implementa la reconocedora ni la multiplicadora.
