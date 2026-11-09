# Proyecto 3: máquinas de Turing

Simulador general de máquinas de Turing deterministas de **una sola cinta**, en
Python 3.11 o posterior. Cada YAML define la máquina y sus entradas. El motor
solo ejecuta transiciones; la multiplicación se resuelve enteramente en la cinta.

## Instalación

Desde la raíz del repositorio, en PowerShell con Python oficial de Windows:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Con Python de MSYS2 (el entorno usado para verificar esta entrega), sustituir el
ejecutable por `.venv/bin/python.exe`. En Linux/macOS usar `.venv/bin/python`.
No hace falta activar el entorno. La única dependencia externa es PyYAML;
las pruebas usan `unittest`.

## Ejecutar las ocho demostraciones

```powershell
.venv\Scripts\python.exe -m src.main examples/reconocedora.yaml --max-steps 10000
.venv\Scripts\python.exe -m src.main examples/multiplicadora.yaml --max-steps 10000
```

Cada comando ejecuta las cuatro entradas del YAML de forma independiente. Muestra
**todas** las descripciones instantáneas, incluida la inicial y la final: paso,
estado, índices de cinta, símbolos y cabezal `^`, incluso sobre blancos o índices
negativos. Después muestra resultado, transiciones aplicadas y cinta final.
Los símbolos aparecen entre comillas para hacer visibles los espacios. La cinta
final omite blancos exteriores y conserva huecos internos; una vacía aparece `''`.

| Máquina | Entrada | Resultado esperado |
| --- | --- | --- |
| Reconocedora | `aabbcc` | Aceptada |
| Reconocedora | `aaabbbccc` | Aceptada |
| Reconocedora | `aabbccc` | Rechazada |
| Reconocedora | `aabcbc` | Rechazada |
| Multiplicadora | `10#11` | Aceptada, cinta `110` |
| Multiplicadora | `11#11` | Aceptada, cinta `1001` |
| Multiplicadora | `101#11` | Aceptada, cinta `1111` |
| Multiplicadora | `101#101` | Aceptada, cinta `11001` |

Un límite agotado se informa como **interrupción**, mostrando la cinta e historial
parciales. Puede aumentarse `--max-steps` para entradas mayores. La multiplicadora
usa sumas repetidas: su tiempo crece con el valor del segundo operando.

Códigos de salida: `0` si todas las entradas terminaron (aceptadas o rechazadas),
`1` si alguna fue interrumpida, `2` ante errores de argumentos, archivo o YAML.
Un rechazo es un resultado válido de simulación. Un símbolo fuera del alfabeto
de entrada es un error de configuración.

## Máquinas y formato YAML

La [reconocedora](docs/reconocedora.md) acepta `a^n b^n c^n`, con `n >= 1`,
mediante marcado. La [multiplicadora](docs/multiplicadora.md) admite `[01]+#[01]+`,
incluidos cero y ceros iniciales. Deja **solo el producto binario canónico** en
la cinta: `0` o una cadena que empieza por `1`, sin separadores ni marcas.

El [formato YAML](docs/formato_yaml.md) especifica los campos `mt` e `inputs`,
las validaciones y las reglas `state/read/write/move/next`. Poner entre comillas
los símbolos y las entradas. Cada símbolo ocupa un carácter; los movimientos
son `L`, `R`, `S`, y el blanco predeterminado es `B`. Se admiten escalares o listas
de un elemento en `read`/`write`; no se admiten listas de varios elementos.
[examples/base.yaml](examples/base.yaml) permite probar una máquina mínima.

## Arquitectura y responsables

| Módulo o entregable | Función | Responsable |
| --- | --- | --- |
| `src/models.py` | Contratos inmutables | J05U3oAr |
| `src/yaml_loader.py` | Carga segura y validación | J05U3oAr |
| `src/tape.py` | Cinta dispersa y snapshots | J05U3oAr |
| `src/simulator.py` | Ejecución general e historial | Alejandro |
| `examples/reconocedora.yaml` | Reconocimiento por transiciones | Alejandro |
| `src/formatter.py` | Presentación de snapshots y resultados | Sebas |
| `src/main.py` | Consola: parser, motor y presentación | Sebas |
| `examples/multiplicadora.yaml` | Multiplicación por transiciones | Sebas |
| Pruebas, README y preparación del video | Verificación y entrega | Cada autor / Sebas |

Consultar [arquitectura y contratos](docs/arquitectura.md). Se conservan las API
de la base y del motor; cada ejecución comienza con una cinta nueva. El generador
opcional `tools/generate_multiplier.py` expande familias de reglas al YAML;
**no participa en la ejecución** y no calcula productos.

## Validación y entrega

Verificación local: **67 pruebas aprobadas** en Python 3.12.7, incluyendo las
50 pruebas que ya tenía el repositorio. La suite incluye parser, modelos, cinta,
motor, reconocedora, visualización, consola y multiplicadora. Esta última se
contrasta con los 256 pares de operandos
de 0 a 15, ceros iniciales, acarreos, entradas mal formadas y limpieza de cinta.
La consola se prueba con ambas máquinas y los ocho casos principales.

Para generar las ocho trazas completas y un resumen reproducible:

```powershell
.venv\Scripts\python.exe tools/export_demonstrations.py
```

Se guardan en `artifacts/demostraciones/` (excluidos de Git). El [guion y lista de
entrega](docs/entrega.md) describe cómo grabar arquitectura y ejecuciones.
**Video pendiente de grabación y publicación no listada**; todavía no existe un
enlace de video para añadir aquí. La integración final corresponde a Alejandro.
