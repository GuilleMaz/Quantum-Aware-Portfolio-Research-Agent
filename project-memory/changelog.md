# Changelog

> Registro cronológico. **Entradas nuevas arriba** (`AGENTS.md` §4).
> Los cambios de diseño van además en `decisions.md`.

---

## 2026-10-18 — Fase 1: fundamentos de MCP (cierre)

### Cambios

- `labs/phase1-mcp-basics/`: experimentos del ciclo `list_tools()` →
  `call_tool()` contra los dos servidores externos.
  - `common.py`, `list_tools.py`, `call_tool.py`, `handshake.py`,
    `bell_circuit.py`, `stateless_demo.py`, `silent_rx_demo.py`,
    `draw_circuit.py`, `probe_financial.py`.
- `snapshots/`: `financial_tools.json` (42 tools), `qiskit_tools.json`
  (13 tools), `get_price_AAPL.json`, `get_fundamentals_AAPL.json`,
  `get_momentum_AAPL.json`, `bell_circuit.json`, `stateless_demo.json`,
  `silent_rx_demo.json`, `bell_circuit_ascii.txt`.
- `docs/mcp-notes.md`: evidencia empírica de Fase 1 (initialize crudo,
  doble encoding con literal, stateless con síntoma literal, fallo silencioso
  de `rx` sin `params`, distribución de Bell).

### Verificación

- `uv sync`: OK, venv Python 3.12.
- `list_tools.py financial`: 42 herramientas.
- `call_tool.py get_price/get_fundamentals/get_momentum AAPL`: `is_error=False`,
  doble encoding parseado en dos pasos.
- `bell_circuit.py`: `{"00": 519, "11": 505}` con 1024 shots (Bell ±5%).
- `stateless_demo.py`: olvidar reenviar el dict crea un circuito nuevo de
  8 qubits con solo `cx` (stateless confirmado).
- `silent_rx_demo.py`: `rx` sin `params` → `params: [0.5]` sin error;
  distribuciones `{"0":961,"1":63}` vs `{"0":769,"1":255}`.
- `draw_circuit.py`: ASCII renderizado con `PYTHONIOENCODING=utf-8`.

### Tareas interactivas pendientes

- 1.15 (Claude Desktop no instalado en este entorno; config de ejemplo lista).
- 1.17/1.18 (verificación manual con el LLM en OpenCode: análisis de ticker
  sin nombrar herramientas y circuito de Bell).

### Motivo

Cerrar la Fase 1 con evidencia reproducible del ciclo MCP y de las dos
trampas centrales (stateless y fallo silencioso), que justifican el reducer
de la Fase 3 y el uso de Qiskit directo (AD-0008).

## 2026-10-18 — Verificación Fase 0: entorno, tests y push

### Cambios

- `uv sync` con Python 3.12: venv funcional, `uv.lock` generado y versionado.
- `pyproject.toml`: sección `[tool.mystnb]` con tabla inline rompía el parseo
  TOML de uv → sustituida por `[tool.myst-nb]` con claves simples.
- `src/quantum_portfolio/models/__init__.py`: importaba `AssetMetrics`, que no
  existe (es `MomentumMetrics`). Corregido y reexportado con `RiskLevel` y
  `Fundamentals`.
- `tests/test_smoke.py`: el test de `TypedDict` usaba `__annotations__`, que
  con `from __future__ import annotations` devuelve strings → cambiado a
  `typing.get_type_hints()`.
- `.gitignore`: `data/` y `outputs/` ignoraban el directorio entero y git no
  veía los `.gitkeep` → cambiado a `data/*` + `!data/.gitkeep` (igual en
  `outputs/`).

### Verificación

- `uv run pytest tests/`: **7 passed**.
- `uv run ruff check src/ tests/`: limpio.
- `uv run mypy src/` (strict): **sin issues en 11 ficheros**.
- Los 5 JSON de `config/` + `opencode.json` parsean con `ConvertFrom-Json`.

### Archivos

- `pyproject.toml`, `.gitignore`, `src/.../models/__init__.py`,
  `tests/test_smoke.py`, `uv.lock`, `data/.gitkeep`, `outputs/.gitkeep`

### Motivo

La Fase 0 no está cerrada hasta que el entorno se verifica ejecutando, no
solo escribiendo ficheros (regla del proyecto: verificar, no asumir).

---

## 2026-10-18 — Fase 0: estructura completa del repo

### Cambios

**Git**
- `git init`, rama `main`, remoto `origin` → GitHub
  (`GuilleMaz/Quantum-Aware-Portfolio-Research-Agent`, ya existía, público).
- `user.name`/`user.email` configurados a nivel de repo (no global).
- `.gitattributes` para normalizar finales de línea (LF en repo, CRLF en
  checkout de Windows).

**Andamiaje**
- `pyproject.toml` con grupos de dependencias: `quantum`, `notebooks`, `data`,
  `dev`. Configuración de `ruff`, `mypy` (strict), `pytest` y `myst-nb`.
- `.gitignore` con regla crítica: **`.env` nunca se commitea**. Excluye
  `data/`, `outputs/`, `*.db` (checkpoints LangGraph), secretos.
- `.python-version` = 3.12.
- `LICENSE` MIT con disclaimer de no-asesoramiento.

**4 archivos raíz (contenido real, no plantillas)**
- `README.md` — qué es, aviso honesto sobre ventaja cuántica, comandos
  verificados, estructura.
- `AGENTS.md` — contrato: stack, comandos, 6 reglas inviolables, trampas
  verificadas, checklist pre-commit.
- `PLAN.md` — 4 fases con objetivo de aprendizaje, entregable, criterio de
  éxito y alcance negativo.
- `TASKS.md` — checklist Fase 0-4 + backlog.

**Memoria del proyecto**
- `project-memory/`: `project-overview.md`, `architecture.md`, `decisions.md`
  (9 decisiones), `changelog.md`, `next-steps.md`.

**Documentación y config** (creados en paralelo por subagente)
- `docs/learning-log.md`, `docs/mcp-notes.md`, `docs/quantum-notes.md`.
- `docs/adr/0001`, `0002`, `0003`.
- `config/mcp_servers.json` + `config/clients/*.example.json` (3 clientes).

**Teoría**
- `theory/` con 12 notebooks MyST.

**Labs**
- `labs/phase1..4-*/README.md` con enlaces a los notebooks que hay que leer
  antes de cada fase.

**Src**
- `src/quantum_portfolio/` con estructura de subpaquetes, **vacía**.

### Archivos
(43 ficheros nuevos)

### Motivo

Establecer la estructura ordenada del repo antes de escribir una línea de
código, con todas las decisiones de diseño ya tomadas y registradas — en lugar
de descubrir los conflicts (`mcp<2`, el archivado de
`langchain-mcp-adapters`, `qiskit-optimization` descontinuado) a mitad de la
Fase 3.

### Verificaciones realizadas antes de decidir

5 subagentes de investigación en paralelo, con verificación empírica
(ejecutando los servidores MCP de verdad, no leyendo solo la documentación):

1. **`financial-mcp-server`**: 42 tools (no 14), datos reales vía yfinance, sin
   API keys, Alpha, 4 meses sin commits. `uvx financial-mcp-server` **roto** →
   `--with "mcp<2"`.
2. **`mcp-qiskit`**: 13 tools, **stateless** (hay que reenviar el dict del
   circuito), `statevector` como strings, gates sin `params` fallan en
   silencio. `uvx mcp-qiskit` **roto** → `--from "mcp-qiskit[mcp]"`.
3. **MCP SDK v2 + LangGraph 1.2**: `FastMCP`→`MCPServer`, `Client` es un
   dataclass con `async with` obligatorio, `langchain-mcp-adapters`
   **archivado**, `ClientSessionGroup` fusiona servidores, LangGraph recomienda
   `TypedDict`. Snippets ejecutados y verificados.
4. **Notebooks de física**: 3 referencias que yo había citado **no existen**;
   sustituidas por Stopfer & Wagner 2025, Certo et al. 2022, Brandhofer et al.
   2022 (verificadas). `qiskit-optimization` descontinuado por IBM.
5. **Configs de cliente**: OpenCode usa `{env:VAR}` y `type: "local"`
   (no `"stdio"`), `/mcps` no `/mcp`, recarga automático. Cursor usa
   `${env:VAR}` y `type: "stdio"`. Claude Desktop no tiene `type`. **Ruta
   absoluta a `uvx.exe` obligatoria** en Windows (verificado con `PATH` mínimo).

### Commits
- `2d10ae6` — chore: estructura base, tooling uv, licencia
- `cf2f63b` — docs: README, AGENTS, PLAN, TASKS

---

## Plantilla

```markdown
## YYYY-MM-DD — Título breve

### Cambios
- Qué se hizo

### Archivos
- Ficheros tocados

### Motivo
- Por qué
```