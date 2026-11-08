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

Preparación inicial del repositorio. Los modelos, el parser y la cinta se
incorporan en los siguientes commits de la base. El motor, la consola y las dos
máquinas corresponden a las siguientes etapas del proyecto.
