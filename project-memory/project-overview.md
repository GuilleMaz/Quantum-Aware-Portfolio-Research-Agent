# Project Overview

> **Fuente de verdad del estado del proyecto.** Si algo aquí contradice a lo que
> crees, este fichero gana. Actualizar tras cada tarea (`AGENTS.md` §4).

---

## Objetivo

Construir un sistema multi-agente orquestado que combina el análisis de datos
de inversión con la simulación de algoritmos cuánticos (QAOA) para explorar
estrategias de cartera.

**El objetivo real es pedagogical:** aprender MCP y orquestación desde dentro,
combinando tres intereses (finanzas, computación cuántica, agentes IA).

**Qué significa "cuántico" aquí:** QAOA sobre problemas de optimización de
carteras (Ising/QUBO). No es criptografía post-cuántica ni blockchain.

---

## Estado Actual

**Fase 0 completa** (2026-10-18). Repo inicializado con la estructura completa,
los 4 archivos raíz, `project-memory/`, `docs/`, `config/`, 12 notebooks en
`theory/`, 4 carpetas en `labs/`, estructura vacía de `src/`, y configs de
ejemplo para 3 clientes MCP.

**Fase 1 (Fundamentos de MCP):** preparada, no iniciada. La carpeta
`labs/phase1-mcp-basics/` existe con su README y checklist.

**Antes de la Fase 1:** leer `theory/index.md.ipynb` para la ruta de lectura, y
`theory/mcp.md.ipynb` + `theory/qiskit-basics.md.ipynb` para el MCP y Qiskit.

---

## Tecnologías

### Stack principal
| Área | Elección | Versión | Nota |
|---|---|---|---|
| Lenguaje | Python | 3.12 | Fijado en `.python-version` |
| Gestor | uv | ≥0.12 | Único gestor; también lanza los MCP servers |
| MCP SDK | `mcp` | ≥2.3.0 | **v2**: `FastMCP` → `MCPServer` |
| Orquestación | `langgraph` | ≥1.2 | Estado con `TypedDict`, no Pydantic |
| Persistencia | `langgraph-checkpoint-sqlite` | ≥3.1 | `AsyncSqliteSaver` |
| Modelos | `pydantic` | ≥2.9 | Solo para datos, no para el estado del grafo |
| Cuántico | `qiskit` + `qiskit-aer` | ≥2.3 / ≥0.17 | **Directo**, no vía MCP |
| Notebooks | `myst-nb` | ≥1.4 | Markdown ejecutable, `.md.ipynb` |
| Análisis | `yfinance`, `pandas`, `numpy`, `scipy` | — | Solo para `theory/` y utilidades |

### Servidores MCP (todos externos, todos Alpha)
| Servidor | Comando verificado | Estado |
|---|---|---|
| `financial-mcp-server` 0.1.12 | `uvx --from financial-mcp-server --with "mcp<2" financial-mcp` | 42 tools, datos reales (yfinance), 1 mantenedor, 4 meses sin commits |
| `mcp-qiskit` 0.1.1 | `uvx --from "mcp-qiskit[mcp]" mcp-qiskit` | 13 tools, **stateless**, 0 estrellas, CI nunca ejecutada |
| `mcp-memory-service` | `uvx --from mcp-memory-service memory server` | Para Fase 4. `mem0-mcp-server` está archivado |

### Clientes MCP soportados
OpenCode (`opencode.json`, `{env:VAR}`, `type: "local"`), Claude Desktop
(`mcpServers`, sin `type`), Cursor (`.cursor/mcp.json`, `${env:VAR}`,
`type: "stdio"`).

---

## Módulos principales

### `theory/` — 12 notebooks (transversales)
Curso completo. Ruta de lectura: `index` → `mcp`/`tool-discovery` →
`python-sdk` → `agents-concepts`/`mcp-agents` → `langgraph` →
`quantum-physics` → `qiskit-basics` → `portfolio-math` → `qaoa` →
`agent-memory`.

**Los tres de física son los que más interesan al usuario:** `quantum-physics.md.ipynb`
(statevector vs density matrix, entrelazamiento, traza parcial, canales CPTP,
T1/T2), `portfolio-math.md.ipynb` (Sharpe, Markowitz, Markowitz → QUBO),
`qaoa.md.ipynb` (Ising → Hamiltoniano, adiabaticidad, supervivencia).

### `labs/` — 4 carpetas de fase
Cuaderno desechable. Se congela al cerrar cada fase.

### `src/quantum_portfolio/` — estructura vacía
Paquete real. Se **promueve** desde `labs/` al cerrar cada fase. Subpaquetes:
`agents/`, `mcp_clients/`, `quantum/`, `graph/`, `models/`.

### `config/` — configuración declarativa
`mcp_servers.json` (fuente única de verdad de los comandos) y `clients/` con
ejemplos para OpenCode, Claude Desktop y Cursor.

---

## Funcionalidades Terminadas

- [x] **Fase 0** — Estructura completa del repo, 4 archivos raíz,
      `project-memory/`, `docs/` (incluidos 3 ADRs), `config/`, 12 notebooks
      `theory/`, 4 carpetas `labs/`, estructura `src/`, `.env.example`,
      `opencode.json`, configs de ejemplo, LICENSE.
- [x] Comandos de los 3 servidores MCP **verificados ejecutando** (no de la
      documentación upstream, que está desactualizada en 2 casos).
- [x] 9 decisiones técnicas documentadas en `decisions.md`.
- [x] 6 referencias académicas verificadas contra Crossref/OpenAlex/arXiv.

---

## Pendientes

### Fase 1 (inmediato)
- [ ] `uv sync` y verificar el venv
- [ ] Handshake `initialize` manual
- [ ] Listar las 42 tools financieras → `snapshots/`
- [ ] 3 llamadas reales a tools (precio, fundamentales, momentum)
- [ ] Circuito de Bell vía `mcp-qiskit` y verificar la distribución
- [ ] **Descubrir que `mcp-qiskit` es stateless** (reenviar el dict)
- [ ] Conectar en OpenCode y Claude Desktop
- [ ] Cerrar la fase y promover a `src/`

### Fases 2-4
- [ ] Fase 2: MCP server propio (`compound_interest`, `loan_emi`, `npv`)
- [ ] Fase 3: cliente multi-servidor + grafo LangGraph lineal y condicional
- [ ] Fase 4: memoria persistente + comparación con CrewAI

### Backlog abierto
- [ ] El tutorial `mcp-intro` citado en el plan original **no existe como repo**.
      Sustituido por los ejemplos oficiales de LangGraph + la spec MCP.
- [ ] Sin wrappers contra los fallos silenciosos de `mcp-qiskit`
- [ ] Sin caché de `get_price_history` (rate limits de Yahoo Finance)

---

## Aviso de Honestidad Científica

Este proyecto **no** demuestra ventaja cuántica en optimización de carteras, y
`README.md` y `theory/qaoa.md.ipynb` §9 lo dicen explícitamente con fuentes.

Con 5–20 activos, $2^{20}$ carteras se enumeran vectorialmente en <1 s.
Stopfer & Wagner (2025) resolvieron 270 instancias reales hasta 1000 activos
con MIP a optimalidad probada en segundos. El Hamiltoniano de coste es
*all-to-all*, lo que en hardware exige un embedding multiplicativo.

**QAOA aquí es un resultado de física valioso y un mal algoritmo de inversión.**
El valor del proyecto es pedagógico y de rigor.