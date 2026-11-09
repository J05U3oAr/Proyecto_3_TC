# Preparación del video y entrega

## Estado real

Consola, visualización y multiplicadora implementadas y verificadas con el motor
existente. README y guion preparados. Pendiente: grabar el video, publicarlo en
YouTube como **no listado** y añadir su URL real al README. Este documento no
constituye evidencia de grabación o publicación. La revisión e integración final
del equipo corresponde a Alejandro.

## Guion sugerido (8–12 minutos)

1. Presentar el proyecto y los responsables. Mostrar que ambas máquinas son YAML
   y comparten parser, cinta y motor. Explicar las reglas de una sola cinta.
2. Mostrar `src/models.py`, `src/yaml_loader.py`, `src/tape.py` y
   `src/simulator.py`: validación, tabla `(estado, símbolo)`, escribir/mover/cambiar
   estado, snapshots independientes y diferencia entre rechazo y límite.
3. Mostrar `src/main.py` y `src/formatter.py`. Explicar índice de cabezal, blanco,
   paso 0, configuración final e historial completo.
4. Ejecutar la reconocedora con el comando del README. Mostrar las cuatro
   entradas: `aabbcc`, `aaabbbccc`, `aabbccc`, `aabcbc`. Para cada una, señalar
   entrada, configuración inicial, evolución y resultado final. Explicar marcado
   y por qué se rechazan los dos últimos casos según `docs/reconocedora.md`.
5. Mostrar las fases de la multiplicadora en `docs/multiplicadora.md` y algunas
   reglas YAML: préstamo, suma con acarreo, marcas, inversión y limpieza.
6. Ejecutar la multiplicadora. Mostrar separadamente `10#11 -> 110`,
   `11#11 -> 1001`, `101#11 -> 1111`, `101#101 -> 11001`. Conservar el historial
   completo en las trazas; se puede recorrer el texto para explicar pasos
   seleccionados y mostrar el final sin leer cientos de líneas en voz alta.
7. Explicar ceros, entradas inválidas, tiempo O((v+1)(a+b)²), espacio de cinta
   lineal y costo de guardar el historial. Mostrar la suite de pruebas pasando.
8. Cerrar con la estructura del repositorio, instalación y comandos reales.

## Evidencias reproducibles

`tools/export_demonstrations.py` ejecuta las dos máquinas usando el motor real,
comprueba los ocho resultados y escribe una traza UTF-8 por entrada, además de
`resumen.json`, en `artifacts/demostraciones/`. No graba pantalla ni publica video.
Los archivos son regenerables y están excluidos de Git.

## Lista para entregar

- Ejecutar `python -m unittest discover -s tests -v` con el entorno instalado.
- Ejecutar `python tools/export_demonstrations.py` y revisar las ocho trazas.
- Grabar pantalla y voz mostrando las ocho ejecuciones y la arquitectura.
- Publicar el video como no listado desde la cuenta del integrante autorizado.
- Comprobar que el enlace abre para quien tenga la URL y añadirlo al README.
- Compartir los enlaces reales de repositorio y video en el medio de entrega.
- Confirmar con el equipo cualquier requisito administrativo del docente.
