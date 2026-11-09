# Contexto e instrucciones para la IA de Alejandro o Sebas

Este documento permite continuar el Proyecto 3 de Teoría de la Computación sin
necesitar el historial del chat original. Trabaja únicamente en las tareas del
integrante que te consulta. Cada tarea tiene un responsable individual.

## 1. Identificar el rol y comprobar el repositorio

1. Identifica si tu usuario es **Alejandro** o **Sebas**. Si no lo indicó, pregunta
   cuál de esos dos roles tiene antes de modificar código.
2. Revisa el estado de Git, los archivos y las instrucciones locales aplicables.
   Conserva los cambios existentes. El repositorio es
   <https://github.com/J05U3oAr/Proyecto_3_TC> y la base se publicó en `master`.
3. Lee [README.md](README.md), [docs/arquitectura.md](docs/arquitectura.md) y
   [docs/formato_yaml.md](docs/formato_yaml.md). Inspecciona los modelos y las API
   reales antes de implementar. Si ya hay trabajo posterior, continúa desde ese
   estado en lugar de asumir que los módulos siguen pendientes.
4. Instala las dependencias y ejecuta las pruebas según el README. Registra los
   fallos previos y distingue los introducidos por tus cambios.
5. Implementa el bloque de tu rol, añade pruebas pertinentes y entrega un resumen
   de archivos, validación y pendientes de integración.

Usa una rama propia, por ejemplo `alejandro/motor-reconocedora` o
`sebas/consola-multiplicadora`, creada desde la base actualizada y con un árbol de
trabajo limpio. Haz commits por bloques funcionales con la identidad Git de tu
usuario. Conserva la autoría de los commits existentes y comunica cualquier
problema de autenticación al subir tu rama. La integración final corresponde a
Alejandro; los commits deben conservar la contribución de cada integrante.

## 2. Objetivo y restricciones del proyecto

Construir un simulador **general de máquinas de Turing deterministas de una sola
cinta** en Python. El programa carga una máquina desde YAML y ejecuta por separado
cada cadena de `inputs`. Debe mostrar el historial completo de descripciones
instantáneas, la cinta final y el resultado de cada ejecución.

Las máquinas elegidas para la evaluación son:

- **Reconocedora:** lenguaje `a^n b^n c^n`, con `n >= 1`. Responsable: Alejandro.
- **Alteradora:** multiplicación de dos números binarios separados por `#`;
  la cinta final contiene únicamente el producto binario. Responsable: Sebas.

El comportamiento de ambas máquinas debe estar descrito en sus transiciones
YAML. El motor ejecuta reglas generales: no reconoce nombres de archivos ni
contiene algoritmos particulares para esos dos problemas. La multiplicación se
resuelve mediante transiciones sobre la cinta, no calculando el producto en
Python y escribiendo la respuesta. Las pruebas sí pueden usar cálculos de Python
como referencia independiente para comparar el resultado.

La entrega requiere cuatro demostraciones de la reconocedora (dos aceptadas y
dos rechazadas), cuatro de la alteradora, todas con entrada de longitud mínima
de cinco, y explicación de la arquitectura. La dificultad de las máquinas forma
parte de la evaluación. Sebas prepara el video y su publicación como no listado
en YouTube; las acciones externas requieren autorización de su usuario.

El enunciado original indica trabajo individual o en parejas; la distribución
de este repositorio contempla tres personas. La autorización del docente para
ese tamaño de grupo sigue siendo una cuestión administrativa del equipo.

## 3. Base ya implementada por J05U3oAr

| Archivo | Función |
| --- | --- |
| `src/models.py` | Modelos y contratos compartidos. |
| `src/yaml_loader.py` | `load_program(path)`, `parse_program(text)` y `ConfigurationError`. |
| `src/tape.py` | `Tape`, cinta dispersa con cabezal y snapshots. |
| `examples/base.yaml` | Ejemplo mínimo para comprobar la infraestructura. |
| `tests/test_models.py`, `tests/test_yaml_loader.py`, `tests/test_tape.py` | Pruebas de la base. |

La base terminó en el commit `ee41cd7`, con 41 pruebas aprobadas en Python 3.13 y
un entorno virtual limpio. Esa cantidad describe aquel punto de partida; los
siguientes commits deben incorporar nuevas pruebas. El proyecto declara soporte
para Python 3.11 o posterior.

Al entregar la base no existían `src/simulator.py`, `src/formatter.py`,
`src/main.py`, `examples/reconocedora.yaml` ni `examples/multiplicadora.yaml`.
Son trabajo pendiente de los roles siguientes. `examples/base.yaml` no sustituye
ninguna máquina evaluada.

Reutiliza la base y conserva sus contratos públicos. Si encuentras un defecto,
reprodúcelo con una prueba y limita la corrección al problema encontrado; explica
el cambio. Acuerda con el usuario cualquier cambio incompatible que obligue al
otro integrante a modificar su implementación.

## 4. Contratos de integración

Las definiciones completas están en `src/models.py` y `docs/arquitectura.md`.
Los puntos necesarios para conectar los módulos son:

- `load_program(path)` devuelve `MachineProgram(machine, inputs)`.
- `machine.transitions` es un mapa de `(estado, símbolo)` a `Transition`.
- La regla tiene `state`, `read`, `write`, `move` y `next_state`. En YAML, el
  último campo se llama `next`; en Python se llama `next_state`.
- `Tape(input_string, blank=machine.blank)` comienza en índice 0, permite índices
  negativos y expone `read()`, `write(symbol)`, `move(direction)`, `snapshot()`,
  `head` y `blank`. Las últimas dos propiedades son de lectura.
- `TapeSnapshot.cells` es una tupla ordenada de pares `(posición, símbolo)` que
  solo almacena celdas no blancas. No es una cadena ni un diccionario.
- Las IDs usan `InstantaneousDescription(step, state, tape)` con un snapshot.
- El resultado usa `SimulationResult(input_string, status, history)`; `history`
  es una tupla no vacía. `final_configuration` devuelve la última ID.
- Los estados son `SimulationStatus.ACCEPTED`, `.REJECTED` y `.STEP_LIMIT`.

API acordada para el motor de Alejandro en `src/simulator.py`:

```python
def simulate(
    machine: TuringMachine,
    input_string: str,
    *,
    max_steps: int = 10_000,
) -> SimulationResult:
    ...
```

Es un contrato pendiente de implementar, no una función disponible en la base.
Para conectar la consola, Sebas importará `simulate` de ese módulo.

El YAML y sus validaciones se especifican en `docs/formato_yaml.md`. Dos detalles
que deben conservarse son los símbolos de un carácter y los movimientos `L`,
`R`, `S`. El blanco predeterminado es `B`. Poner entre comillas símbolos binarios,
el separador `#` y las entradas para evitar conversiones de YAML.

El PDF muestra listas ambiguas como `read: [a, B]`, aunque exige una cinta.
La decisión actual admite escalares o listas de un elemento en `read`/`write` y
rechaza listas de varios elementos. Es una convención documentada del proyecto,
no una aclaración oficial del docente. No cambies esa interpretación silenciosamente.

## 5. Trabajo exclusivo de Alejandro

Implementa las tareas A1–A5 en este orden. La consola y la multiplicadora siguen
siendo responsabilidad de Sebas.

| Tarea | Entregable | Criterio de finalización |
| --- | --- | --- |
| A1. Motor | `src/simulator.py` | Implementa `simulate` sobre la cinta y las reglas validadas; crea una cinta nueva por llamada y conserva una ID por paso. |
| A2. Terminación y pruebas | `tests/test_simulator.py` | Verifica aceptación, falta de regla, límite de pasos, estado inicial final, entradas vacías e independencia entre ejecuciones. |
| A3. Reconocedora | `examples/reconocedora.yaml` | Reconoce exactamente `a^n b^n c^n`, con `n >= 1`, mediante transiciones de una cinta. |
| A4. Pruebas y explicación | `tests/test_reconocedora.py`, `docs/reconocedora.md` | Verifica los cuatro casos principales y casos límite; explica fases, marcas, estados y complejidad del algoritmo implementado. |
| A5. Integración final | Pruebas de integración y correcciones necesarias | Cuando esté disponible la rama de Sebas, integra conservando los commits y verifica la consola con ambas máquinas y los ocho casos principales. |

Semántica que debe cumplir el motor:

1. Comenzar en paso 0, estado inicial y cabezal en 0; guardar la ID inicial.
2. Si el estado actual es de aceptación, devolver `ACCEPTED`.
3. Si no hay transición aplicable en un estado no final, devolver `REJECTED`.
4. Si aún se requiere una transición y se agotó el presupuesto, devolver
   `STEP_LIMIT`. El presupuesto cuenta transiciones aplicadas, no IDs.
5. En otro caso, escribir, mover, cambiar de estado, incrementar el paso,
   guardar un snapshot independiente y repetir.

Ese orden permite aceptar en el paso 0 o exactamente en el último paso permitido,
y distinguir una detención por falta de regla de una interrupción por presupuesto.
Valida que el límite sea un entero no negativo. El motor también debe rechazar
como error de uso una llamada directa con símbolos fuera del alfabeto de entrada.

Para la reconocedora, comprueba también cadena vacía, bloques faltantes, cantidades
distintas y símbolos en orden incorrecto dentro de su alfabeto. Una estrategia
por marcado permite justificar tiempo cuadrático y espacio lineal; la explicación
debe corresponder a las transiciones que realmente se implementen.

Si Sebas aún no terminó, completa A1–A4 y comunica que A5 depende de su rama;
no implementes su trabajo para cerrar anticipadamente la integración.

## 6. Trabajo exclusivo de Sebas

Implementa las tareas S1–S5. El motor y la reconocedora siguen siendo
responsabilidad de Alejandro.

| Tarea | Entregable | Criterio de finalización |
| --- | --- | --- |
| S1. Visualización | `src/formatter.py`, `tests/test_formatter.py` | Muestra IDs completas con paso, estado, cinta y posición inequívoca del cabezal, incluso sobre blancos o índices negativos. |
| S2. Consola | `src/main.py`, `tests/test_cli.py` | Permite `python -m src.main ruta.yaml --max-steps 10000`, ejecuta cada entrada con el motor de Alejandro y muestra resultado y cinta final. |
| S3. Multiplicadora | `examples/multiplicadora.yaml` | Realiza la multiplicación binaria mediante reglas de una cinta y termina dejando solo el producto, sin operandos ni marcas auxiliares. |
| S4. Pruebas y explicación | `tests/test_multiplicadora.py`, `docs/multiplicadora.md` | Verifica los cuatro productos principales y casos límite; documenta formato de operandos, ceros, fases, acarreos y limpieza. |
| S5. Documentación y video | README final, guion y enlace de entrega | Documenta los comandos reales y las dos máquinas; graba ocho ejecuciones y arquitectura, y prepara la publicación no listada y el enlace con la autorización de su usuario. |

La visualización debe incluir la configuración inicial y la final, conservar el
historial completo y distinguir aceptada, rechazada e interrumpida por límite.
Para dibujar la cinta, incluye el cabezal y las celdas no blancas; una cinta vacía
debe mostrar al menos una celda blanca. La consola debe presentar errores útiles
de archivo y configuración.

Si el motor aún no está disponible, empieza por el formateador, sus pruebas con
modelos construidos directamente, el diseño de la máquina y su documentación.
Informa la dependencia para las pruebas de ejecución; conserva un único motor,
propiedad de Alejandro, y no presentes una simulación completa hasta integrarlo.

Define explícitamente qué representaciones binarias admite la multiplicadora y
cómo trata el cero y los ceros iniciales. La salida debe coincidir con esa política.
Justifica su dificultad a partir del algoritmo implementado; su complejidad
temporal debe considerar los recorridos de una sola cinta, no el costo de una
multiplicación nativa de Python.

## 7. Casos principales de demostración

| Máquina | Entrada | Resultado esperado |
| --- | --- | --- |
| Reconocedora | `aabbcc` | Aceptada. |
| Reconocedora | `aaabbbccc` | Aceptada. |
| Reconocedora | `aabbccc` | Rechazada. |
| Reconocedora | `aabcbc` | Rechazada. |
| Multiplicadora | `10#11` | `110` (2 por 3). |
| Multiplicadora | `11#11` | `1001` (3 por 3). |
| Multiplicadora | `101#11` | `1111` (5 por 3). |
| Multiplicadora | `101#101` | `11001` (5 por 5). |

Estos casos tienen entradas de longitud mínima de cinco. Son las demostraciones
principales, no la totalidad de las pruebas necesarias para validar cada máquina.

## 8. Cierre de cada bloque

Antes de registrar un bloque, ejecuta las pruebas pertinentes y la suite existente
según el README. Comprueba que el diff corresponda al rol, que no se incluyan
entornos virtuales o credenciales y que la documentación describa el comportamiento
real. No reduzcas pruebas existentes para ocultar fallos.

Al responder al usuario, indica qué tareas completaste, qué archivos cambiaste,
qué pruebas ejecutaste, los commits creados y las dependencias todavía pendientes.
Una entrega parcial por dependencia debe identificarse como tal.

## 9. Mensajes para adjuntar este archivo a otra IA

**Alejandro:**

> Soy Alejandro. Lee INSTRUCCIONES_IA.md y los documentos que referencia. Implementa
> únicamente mis tareas, comenzando por el motor. Conserva la base existente,
> añade pruebas y haz commits por bloques terminados. Deja la consola y la
> multiplicadora para Sebas. Si su rama aún no está disponible, informa la
> dependencia de integración.

**Sebas:**

> Soy Sebas. Lee INSTRUCCIONES_IA.md y los documentos que referencia. Implementa
> únicamente mis tareas. Conserva la base y el contrato del motor de Alejandro,
> añade pruebas y haz commits por bloques terminados. Empieza por la visualización
> y el diseño de la multiplicadora si el motor todavía no está disponible.

Adjuntar este archivo da contexto; la IA necesita también acceso al repositorio
o a sus archivos para inspeccionar el código y ejecutar las pruebas.
