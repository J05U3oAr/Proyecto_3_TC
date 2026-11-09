# Multiplicadora binaria de una cinta

## Contrato

`examples/multiplicadora.yaml` acepta exactamente `[01]+#[01]+`. Los operandos
son binarios sin signo, más significativo primero. Permite `0`, `000` y ceros
iniciales; rechaza operandos vacíos, separadores repetidos y la cadena vacía.
Los símbolos ajenos a `0`, `1`, `#` producen error del parser antes de simular.
La salida es el producto binario canónico, sin ceros iniciales salvo el único
`0` que representa cero. Puede quedar en índices distintos del cero: solo existe
una secuencia contigua de bits; todas las otras celdas están blancas.

Se usan 40 estados y 163 transiciones explícitas. Hay un único cabezal y una única
cinta; no se utilizan multiplicación nativa, llamadas externas ni varias pistas.
`tools/generate_multiplier.py` permite regenerar el YAML sin escribir a mano las
familias de reglas. El motor solo carga el YAML ya generado.

## Fases e invariantes

1. **Validar y preparar.** `start`, `sentinel`, `validate_a`, `first_b` y
   `validate_b` verifican ambos bloques. La cinta queda `^A#C$0`: `^` delimita el
   extremo izquierdo, `C` es el segundo operando y tras `$` está el acumulador.
   La validación ocurre antes de iniciar las operaciones aritméticas.
2. **Descontar una iteración.** `decrement` resta uno a `C` desde su extremo
   derecho: cambia ceros por unos hasta encontrar un uno que cambia a cero.
   Si llega a `#`, el contador era cero: termina la suma repetida. En ese caso
   los unos producidos por el préstamo se borrarán en la limpieza.
3. **Sumar A.** `pick_0` y `pick_1` recuerdan el acarreo en el estado. Recorren
   `A` de derecha a izquierda; marcan sus bits `0/1` como `x/y`. Por cada bit,
   `go_bit_carry` cruza el contador hasta `$`; `add_bit_carry` salta los bits del
   acumulador ya procesados (`u/v`, que representan `0/1`). El acumulador se
   almacena **menos significativo primero**, para extenderlo hacia la derecha.
   El estado implementa la tabla finita de suma de tres bits: bit de A, bit del
   acumulador y acarreo. Un blanco del acumulador vale cero. `return_0/1` regresa
   a `#` conservando el nuevo acarreo.
4. **Resolver acarreo y restaurar.** Al llegar a `^`, `finish_0/1` conduce a
   `carry_0/1`. Si sobra acarreo, unos consecutivos se convierten en ceros hasta
   escribir uno en un cero o blanco. `restore_acc` recupera `u/v -> 0/1`;
   `restore_a` recupera `x/y -> 0/1`. `next_round` vuelve a descontar el contador.
   Tras k rondas completas, el acumulador vale k veces A y el contador vale
   el segundo operando menos k. A conserva su valor y su longitud.
5. **Invertir.** Cuando el contador era cero, `finish_seek` escribe `@` tras el
   acumulador. `reverse_pick` toma el bit sin marcar más a la derecha, lo marca
   y lo copia al final de la región situada tras `@` usando `reverse_seek_0/1`,
   `append_0/1` y `reverse_back`. Así la copia queda más significativo primero.
6. **Limpiar y normalizar.** `erase_left` borra operandos y `^`.
   `erase_right` borra `$`, acumulador y `@`. `trim` borra ceros iniciales de la
   copia; al encontrar un uno acepta. Si todos eran ceros, `zero` escribe un
   único cero y acepta. No sobreviven marcas, huecos internos ni operandos.

La dificultad procede de transportar bits y acarreos con recorridos de un solo
cabezal, preservar el operando para otra ronda y revertir/limpiar el resultado.
La tabla de transiciones es el algoritmo completo.

## Complejidad

Sean a y b las longitudes de los operandos, v el valor numérico del segundo y
w = a + b. El producto necesita como máximo w bits. Cada suma procesa a bits;
para cada uno recorre una zona de O(w) celdas. El decremento, restauración y
acarreo cuestan O(w) por ronda. La inversión final cuesta O(w²). Una cota
temporal total es **O((v + 1) w²)** transiciones, y el espacio de cinta es
**O(w)**. El tiempo puede ser exponencial en b porque v puede llegar a 2^b - 1;
no se presenta como una multiplicación de tiempo polinómico. El contador es el
operando derecho, por lo que intercambiar operandos puede cambiar mucho el tiempo.

Estas cotas describen la MT. El simulador guarda T+1 snapshots: usa O(Tw) memoria
para el historial y además ordena las celdas en cada snapshot. Un límite de pasos
interrumpe sin fingir aceptación ni rechazo, y puede dejar marcas temporales.

## Comprobación

Las cuatro demostraciones usan respectivamente 227, 248, 321 y 557 transiciones
y producen `110`, `1001`, `1111`, `11001`. `tests/test_multiplicadora.py` compara
todos los 256 pares entre 0 y 15 con una referencia de Python, comprueba ceros,
ceros iniciales, acarreos, rechazo de entradas mal formadas y ausencia de residuos.
También verifica que cada cambio del historial corresponde exactamente a la regla
YAML aplicable. Las operaciones de Python usadas como referencia pertenecen solo
a las pruebas, no a la simulación.
