# Formato YAML de una máquina de una cinta

El archivo tiene dos campos en la raíz: `mt` e `inputs`. Se rechazan claves
desconocidas o repetidas para detectar errores de escritura.

```yaml
mt:
  states: [q0, qf]
  input_alphabet: ["a"]
  tape_alphabet: ["a", "B"]
  initial_state: q0
  accept_states: [qf]
  blank: "B"
  transitions:
    - state: q0
      read: "a"
      write: "a"
      move: R
      next: q0
    - state: q0
      read: "B"
      write: "B"
      move: S
      next: qf
inputs: ["", "a", "aaa"]
```

## Campos y validaciones

| Campo | Reglas |
| --- | --- |
| `mt.states` | Lista no vacía de nombres de estado, sin duplicados. |
| `mt.input_alphabet` | Lista de caracteres únicos; puede estar vacía si solo se procesa la cadena vacía. |
| `mt.tape_alphabet` | Lista no vacía de caracteres únicos; incluye el alfabeto de entrada y el blanco. |
| `mt.initial_state` | Nombre de un estado declarado. |
| `mt.accept_states` | Lista de estados declarados, sin duplicados; puede estar vacía. |
| `mt.blank` | Opcional: un carácter, `B` por defecto. Debe estar en el alfabeto de cinta y fuera del de entrada. |
| `mt.transitions` | Lista de reglas; puede estar vacía y no tiene que cubrir todas las combinaciones. |
| `inputs` | Lista no vacía de cadenas; sus símbolos pertenecen al alfabeto de entrada. Se conserva el orden y se permiten entradas repetidas. |

Cada regla contiene exactamente `state`, `read`, `write`, `move`, `next`.
`state` y `next` deben ser estados declarados. `read` y `write` son caracteres del
alfabeto de cinta. `move` acepta `L`, `R` y `S` (sin movimiento). No puede haber dos
reglas con el mismo par `(state, read)`, aunque sus resultados sean iguales.

Cada símbolo ocupa un carácter Unicode de Python (`len(symbol) == 1`); no se
admiten tokens de varios caracteres. La entrada vacía se escribe `""`. Un espacio
puede ser símbolo si se declara entre comillas. Se usa una cinta extendible hacia
ambos lados, cabezal inicial en índice 0 y entrada escrita desde ese índice.

Poner **entre comillas todos los símbolos y las entradas**, especialmente `"0"`,
`"1"`, `"#"` y valores como `"Y"`. PyYAML puede interpretar ciertos textos sin
comillas como números, booleanos o comentarios; el parser exige los tipos
correctos y no realiza conversiones silenciosas.

## Decisión sobre el ejemplo del enunciado

El PDF exige una sola cinta, pero presenta campos como `read: [a, B]` y
`write: [a, B]` sin aclarar qué representa cada posición. La base adopta
explícitamente un símbolo leído y uno escrito por transición:

- Formato recomendado: `read: "a"` y `write: "X"`.
- También se aceptan listas de un elemento: `read: ["a"]`, `write: ["X"]`.
- Las listas vacías o de varios elementos producen `ConfigurationError`.
  No se ignoran posiciones ni se interpretan como varias cintas.

Esta es una decisión de implementación documentada, **no una aclaración del
docente**. Conviene confirmar la notación si se exige cargar literalmente el
ejemplo del PDF. `blank` explícito y el movimiento `S` son convenciones adicionales
de esta base; `blank` puede omitirse y se pueden usar solo `L`/`R`.

## API y errores

```python
from src.yaml_loader import ConfigurationError, load_program

try:
    program = load_program("examples/base.yaml")
except ConfigurationError as error:
    print(error)
```

`parse_program(text)` ofrece las mismas validaciones sobre texto en memoria.
La carga usa un derivado de `yaml.SafeLoader`, rechaza claves duplicadas y
no admite etiquetas que construyen objetos Python arbitrarios. Un archivo debe
contener un único documento YAML en UTF-8, con o sin BOM.

La base únicamente carga y valida. La aceptación y el rechazo de una cadena
válida se determinarán en el motor de Alejandro. Una entrada con símbolos fuera
del alfabeto constituye un error de configuración, no un rechazo simulado.
