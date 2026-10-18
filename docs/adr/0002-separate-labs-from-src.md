# ADR 0002 — Separar `labs/` de `src/`

- **Estado:** aceptado
- **Fecha:** 2026-10-18

## Contexto

El código de aprendizaje (feo, desechable, sin tests, que existe para entender
el protocolo tocándolo) y el paquete real (importable, testeado, que otros
módulos consumen) tienen ciclos de vida opuestos. Mezclados en un solo sitio,
el paquete acaba lleno de scripts de tutorial y la cobertura de tests no
significa nada.

## Decisión

- `labs/` = cuaderno desechable, una carpeta por fase, con su README y sus
  snapshots. Se congela al cerrar cada fase y no se toca más.
- `src/quantum_portfolio/` = paquete real. Se puebla por **promoción** desde
  `labs/` al cerrar cada fase: se reescribe limpio y con tests.
- No se escribe directamente en `src/` durante el aprendizaje.

## Consecuencias

- `ruff` y `mypy` aplican reglas relajadas en `labs/` y estrictas en `src/`
  (ver `pyproject.toml`).
- `tests/` solo cubre `src/`, nunca `labs/`.
- La promoción es manual y explícita: al cerrar cada fase hay una tarea
  `TASKS.md` que lo exige.

## Alternativas

- **Un solo `src/` con subcarpetas por fase:** un solo lugar, pero el paquete
  se llena de código de tutorial y los tests se mezclan con experiments.
- **Solo `labs/`, sin `src/` todavía:** máximo foco en aprender, pero obliga a
  reescribir todo al final cuando se quiera empaquetar.
