# Máquina reconocedora de `a^n b^n c^n`

La máquina acepta exactamente `a^n b^n c^n` para `n >= 1`. Usa una cinta y
marca cada terna emparejada como `X`, `Y`, `Z`.

## Fases

- `q0` busca la primera `a` sin marcar y la cambia por `X`.
- `find_b` avanza por las `a` restantes y las `Y` hasta encontrar una `b`, que
  cambia por `Y`.
- `find_c` avanza sobre `b` restantes y `Z` hasta hallar una `c`, que cambia
  por `Z`.
- `return_left` retrocede hasta el blanco previo a la entrada y vuelve a `q0`.
- Cuando ya no hay `a`, `check_tail` permite solo `Y` y `Z` hasta el blanco.
  La máquina no tiene transición para `q0` sobre blanco, de modo que la cadena
  vacía se rechaza y la fase terminal solo se alcanza después de marcar al menos
  una terna.

El tiempo es `O(n²)`: se hacen `n` pasadas de ida y vuelta sobre una cinta de
longitud `3n`. La cinta usa `O(n)` celdas; las marcas reemplazan los símbolos y
no requieren espacio auxiliar fuera de la entrada.

Los casos de demostración y los límites están en `tests/test_reconocedora.py`.
