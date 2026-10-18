# Changelog

> Registro cronológico. **Entradas nuevas arriba** (`AGENTS.md` §4).
> Los cambios de diseño van además en `decisions.md`.

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