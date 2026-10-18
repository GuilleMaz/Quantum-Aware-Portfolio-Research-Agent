# Architecture

> Estructura, componentes y flujo de datos. Actualizar cuando cambie el diseño
> estructural (`AGENTS.md` §4).

---

## Estructura

```
Quantum-Aware Portfolio Research Agent/
├── AGENTS.md              Contrato de trabajo (leer primero)
├── README.md              Qué es esto + quickstart + aviso honesto
├── PLAN.md                Roadmap de las 4 fases
├── TASKS.md               Checklist ejecutable (1 tarea = 1 commit)
├── opencode.json          Config MCP de OpenCode (sintaxis {env:VAR})
├── pyproject.toml         uv + deps por grupo + ruff/mypy/pytest
├── .python-version        3.12
│
├── project-memory/        ESTA CARPETA — fuente de verdad del estado
│   ├── project-overview.md
│   ├── architecture.md        ← este fichero
│   ├── decisions.md
│   ├── changelog.md
│   └── next-steps.md
│
├── theory/                12 notebooks MyST (.md), curso transversal
│   └── figures/           Imágenes extraídas de los notebooks
│
├── labs/                  Experiments por fase (cuaderno desechable)
│   ├── phase1-mcp-basics/
│   │   └── snapshots/     Salidas reales commiteadas (evidencia)
│   ├── phase2-own-server/
│   ├── phase3-langgraph/
│   └── phase4-memory-crewai/
│
├── src/quantum_portfolio/ Paquete real (estructura vacía en Fase 0)
│   ├── agents/            financial_analyst, quantum_researcher, memory
│   ├── mcp_clients/       session_group.py — ÚNICA capa que habla MCP
│   ├── quantum/           qaoa.py, simulator.py — motor con Qiskit directo
│   ├── graph/             state.py, nodes.py, edges.py, build.py
│   ├── models/            Esquemas Pydantic (Asset, Metrics, Portfolio)
│   └── cli.py
│
├── tests/                 Tests del paquete src/ (NO de labs/)
├── scripts/               Bootstrap, sync de config, checks
├── notebooks/             Exploración libre (diferente de theory/)
│
├── docs/
│   ├── learning-log.md    Bitácora de aprendizaje (qué se aprendió)
│   ├── mcp-notes.md       Cuaderno del protocolo MCP
│   ├── quantum-notes.md   Cuaderno de física cuántica
│   └── adr/               Architecture Decision Records
│
├── config/
│   ├── mcp_servers.json   Fuente única de verdad de los comandos MCP
│   └── clients/           *.example.json para OpenCode/Claude/Cursor
│
├── data/                  Cache de precios (gitignored, con .gitkeep)
└── outputs/               Informes generados (gitignored, con .gitkeep)
```

---

## Componentes

### Capa 1 — `theory/` (conocimiento, no código)
12 notebooks MyST Markdown ejecutables. Transversales a las fases: no están
atados a una, cada README de fase enlaza a los que hay que leer antes.

**Notebooks de física** (los que más interesan al usuario, que es físico):
- `quantum-physics.md` — statevector vs density matrix, estados producto
  vs entrelazados, traza parcial, valor esperado, canales CPTP, T1/T2, NISQ.
- `portfolio-math.md` — retorno, covarianza, Sharpe y sus sesgos,
  Markowitz con Lagrange, frontera eficiente, conditioning de Σ, **Markowitz →
  QUBO**.
- `qaoa.md` — Ising ↔ QUBO ↔ Hamiltoniano, $H_C$ diagonal, por qué
  $|+\rangle^{\otimes n}$ es el estado fundamental de $-H_M$, el ansatz,
  adiabaticidad, principio de variación, QAOA como distribución, barren
  plateaus, **§9 supervivencia con 5 argumentos y fuentes**.

### Capa 2 — `labs/` (experimentos)
4 carpetas, una por fase. Cada una con `README.md` que enlaza a su `theory/` y
la lista de tareas. Puede estar feo. **Se congela al cerrar la fase.**

### Capa 3 — `src/quantum_portfolio/` (paquete)
Vacía en Fase 0. Se puebla por **promoción** desde `labs/` al cerrar cada fase,
ya limpio y con tests.

### Capa 4 — `config/` (declarativo)
`mcp_servers.json` es la fuente única de verdad: tanto el cliente MCP como
`src/quantum_portfolio/mcp_clients/` leen de ahí. Los `config/clients/*.example.json`
son traducciones de esa misma fuente a la sintaxis de cada cliente.

---

## Flujo de datos del sistema (objetivo, tras Fase 3)

```
config/mcp_servers.json
        │
        ▼
┌───────────────────────────────────────────┐
│  mcp_clients/session_group.py             │
│  ClientSessionGroup (MCP SDK v2)          │
│  fusiona tools de N servidores            │
│  prefija nombres para evitar colisiones   │
└───────────────┬───────────────────────────┘
                │  list[BaseTool]
                ▼
┌───────────────────────────────────────────┐
│  graph/state.py  (TypedDict)              │
│  cartera, metricas, alta_volatilidad,    │
│  circuito_qiskit, recomendacion          │
└───────────────┬───────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────┐
│  graph/nodes.py                           │
│  analizar_activos ─┐                     │
│                     ├─ conditional ─┐    │
│  analisis_clasico ◄┤                │    │
│  optimizacion_robusta (QAOA) ◄───────┘    │
│  generar_recomendacion                     │
└───────────────┬───────────────────────────┘
                │
                ▼
      AsyncSqliteSaver (thread_id)  →  outputs/
```

---

## Servicios

| Servicio | Puerto | Autenticación | Notas |
|---|---|---|---|
| `financial-mcp` | — (stdio) | Ninguna | Solo `FRED_API_KEY` opcional (4 tools macro) |
| `mcp-qiskit` | — (stdio) | Ninguna | `IBM_QUANTUM_TOKEN` opcional, inalcanzable hoy |
| `mcp-memory-service` | — (stdio) | Ninguna | Fase 4. Self-hosted |
| MCP server propio | — (stdio) | — | Fase 2 |
| Qiskit Aer | — (in-process) | — | **No** es un servicio: es una librería |

**Todos los MCP son stdio.** Ninguno abre un puerto. El proceso lo lanza el
cliente, y muere cuando el cliente cierra el scope (OpenCode mata el process
group completo).

---

## Dependencias

### Críticas (el proyecto no funciona sin ellas)
- `mcp>=2.3.0` — SDK oficial v2. **`FastMCP` → `MCPServer`.**
- `langgraph>=1.2` — grafos de estado.
- `qiskit>=2.3` + `qiskit-aer>=0.17` — motor cuántico real.
- `langgraph-checkpoint-sqlite>=3.1` — persistencia de estado.

### Opcionales por grupo
`--extra quantum` (Qiskit+matplotlib), `--extra notebooks` (MyST-NB),
`--extra data` (yfinance/pandas/scipy), `--extra dev` (pytest/ruff/mypy).

### Conflictos y trampas de dependencias

| Conflicto | Resolución |
|---|---|
| `mcp 2.x` rompe `financial-mcp-server` y `mcp-qiskit` | `--with "mcp<2"` en el comando de arranque |
| `langchain-mcp-adapters` pinea `mcp<2` y está **archivado** | No se usa. Cliente MCP propio (~30 líneas) |
| `qiskit-optimization` **descontinuado por IBM** | QUBO construido a mano con numpy |
| `mcp-qiskit` pinea `qiskit==2.3.1` exacto | Se usa `uvx` (entorno aislado), no el venv del proyecto |
| `mcp-qiskit` devuelve `statevector` como strings | Usar Qiskit directo para valores esperados |
| Windows: clientes GUI tienen `PATH` mínimo | **Ruta absoluta** a `uvx.exe` en los configs de cliente |
| Python 3.13 en el sistema vs 3.12 en el proyecto | uv descarga 3.12 según `.python-version` |

---

## Reglas estructurales

1. **Ningún `print` a stdout en un servidor MCP.** Rompe el protocolo JSON-RPC.
   A `stderr`.
2. **Toda llamada MCP vive en `src/quantum_portfolio/mcp_clients/`.**
3. **El estado del grafo es `TypedDict`, no Pydantic.** Pydantic solo para los
   esquemas de datos (`Asset`, `Metrics`, `Portfolio`).
4. **Los comandos de los servidores MCP salen de `config/mcp_servers.json`,**
   nunca hardcodeados.
5. **Los tickers y el universo de activos viven en `config/`,** no en el
   servidor MCP (que no tiene ninguna tool para devolver un universo).
6. **El motor cuántico es Qiskit directo.** MCP es la capa de orquestación.
7. **Nada de secretos en el repo.** `.env` está en `.gitignore`.