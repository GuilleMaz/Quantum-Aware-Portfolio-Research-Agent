# ADR 0001 — Adoptar registro de decisiones (ADR)

- **Estado:** aceptado
- **Fecha:** 2026-10-18
- **Contexto en:** `project-memory/decisions.md` (AD-0001..AD-0009)

## Contexto

Hay tres ficheros de memoria con roles que se solaparían si no se separan:

- `project-memory/changelog.md` — qué cambió y cuándo.
- `project-memory/decisions.md` — qué se decidió y por qué.
- `docs/learning-log.md` — qué se aprendió.

Sin una convención explícita, las decisiones acaban enterradas en el changelog
o repetidas en los tres sitios.

## Decisión

Adoptar Architecture Decision Records numerados en `docs/adr/` con formato
estándar (Estado / Contexto / Decisión / Consecuencias / Alternativas) para las
decisiones estructurales, y mantener `project-memory/decisions.md` como índice
resumido con las 9 decisiones verificadas.

## Consecuencias

- Cada decisión estructural tiene un fichero propio citable (`docs/adr/NNNN-*.md`).
- `decisions.md` sigue siendo la lectura rápida; los ADR son el detalle.
- El changelog no contiene decisiones, solo las referencia.

## Alternativas

- **Solo `decisions.md`, sin ADR:** menos ficheros, pero las decisiones largas
  (p. ej. separar `labs/` de `src/`) no caben en un índice sin romperlo.
- **Decisiones dentro del changelog:** el changelog se vuelve ilegible y las
  decisiones no se encuentran.
