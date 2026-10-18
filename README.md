# Quantum-Aware Portfolio Research Agent

Sistema multi-agente orquestado que combina análisis financiero con simulación
cuántica (QAOA) para explorar estrategias de cartera.

> **Esto es un proyecto de aprendizaje.** No es asesoramiento financiero. Las
> carteras simuladas y los resultados aquí producidos no constituyen
> recomendación de inversión alguna.

---

## Qué es esto

Un grafo de agentes donde un **Analista Financiero** obtiene precios,
fundamentales y métricas de riesgo vía MCP; un **Investigador Cuántico**
formula el problema de optimización como un circuito QAOA vía MCP; y un
**Orquestador** en LangGraph decide el flujo entre ambos.

```
                    ┌──────────────────┐
                    │   Orquestador    │
                    │    (LangGraph)   │
                    └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
   │  Analista   │    │ Investigador │    │Recomendador │
   │  Financiero │    │   Cuántico   │    │             │
   └──────┬──────┘    └──────┬───────┘    └─────────────┘
          │                  │
          ▼                  ▼
   ┌─────────────┐    ┌──────────────┐
   │ financial-  │    │  mcp-qiskit  │
   │ mcp-server  │    │              │
   └─────────────┘    └──────────────┘
        MCP                    MCP
```

---

## Aviso honesto sobre el resultado científico

Este repositorio **no** pretende demostrar ventaja cuántica en optimización de
carteras. La evidencia publicada dice lo contrario, y el proyecto lo asume y lo
documenta:

- Con 5–20 activos, $2^{20} = 1{,}048{,}576$ carteras se enumeran vectorialmente
  en **menos de un segundo** en un portátil.
- Stopfer & Wagner (arXiv:2509.17876, 2025) resolvieron 270 instancias reales
  hasta **1000 activos con MIP a optimalidad probada en segundos**.
- El Hamiltoniano de coste de un portfolio es *all-to-all* (Σ es densa), lo que
  en hardware exige un embedding que multiplica qubits y profundidad.

**QAOA aquí es un gran resultado de física y un mal algoritmo de inversión.**
El valor del proyecto es pedagógico y de rigor: entender el protocolo MCP, la
orquestación con grafos de estado, y la física de QAOA a fondo. La sección
`theory/qaoa.md` §9 desarrolla los cinco argumentos con referencias
verificadas.

---

## Estructura del repo

```
├── AGENTS.md              Contrato: cómo trabaja cualquier IA/agente aquí
├── PLAN.md                Roadmap de las 4 fases
├── TASKS.md               Checklist ejecutable (1 tarea = 1 commit)
├── theory/                12 notebooks: curso teórico transversal
├── labs/                  Experiments por fase (cuaderno desechable)
├── src/quantum_portfolio/ Paquete real (lo que se importa y se testea)
├── project-memory/        Memoria persistente del proyecto
├── docs/                  Conocimiento no-code + ADRs
└── config/                Config declarativa de servidores MCP
```

**El principio:** `labs/` es el cuaderno y puede estar feo. `src/` es el paquete
que se importa y se testea. El código se **promueve** de `labs/` a `src/` al
cerrar cada fase.

Detalle completo en [`project-memory/architecture.md`](project-memory/architecture.md).

---

## Requisitos

- **Python 3.12** (fijado en `.python-version`; uv lo instala si falta)
- **uv** ≥ 0.12 — https://docs.astral.sh/uv/
- **git**

```powershell
winget install --id=astral-sh.uv
```

---

## Quickstart

```powershell
# 1. Entorno con las dependencias base
uv sync

# 2. Añadir lo que necesites según la fase
uv sync --extra notebooks     # motor de los notebooks de theory/
uv sync --extra quantum       # Qiskit para el motor cuántico real
uv sync --extra data          # yfinance/pandas para análisis

# 3. Conectar los servidores MCP al cliente (ver config/clients/)
#    OpenCode: ya incluido en opencode.json
#    Claude Desktop: copiar config/clients/claude_desktop_config.example.json
#    Cursor: copiar config/clients/cursor.example.json

# 4. Empezar por la teoría, no por el código
#    Lee theory/index.md
```

**Aviso de rendimiento:** el servidor `mcp-qiskit` tarda **67 s en el primer
arranque** (descarga 97 paquetes) y ~9 s en caliente. Por eso la configuración
de OpenCode lleva `timeout: 60000` en lugar del default de 5000 ms.

---

## Los servidores MCP

| Servidor | Comando verificado | Notas |
|---|---|---|
| **financial-mcp-server** | `uvx --from financial-mcp-server --with "mcp<2" financial-mcp` | 42 herramientas, datos reales vía yfinance. **42, no 14.** |
| **mcp-qiskit** | `uvx --from "mcp-qiskit[mcp]" mcp-qiskit` | 13 herramientas. **Stateless**: hay que reenviar el dict del circuito en cada llamada. |
| **propio (Fase 2)** | `uv run mcp dev src/...` | El que escribimos para entender el protocolo desde dentro |
| **mcp-memory-service** | `uvx --from mcp-memory-service memory server` | Sustituye a `mem0-mcp-server`, cuyo repo está archivado |

**Por qué `--with "mcp<2"`:** ambos paquetes externos declaran `mcp[cli]>=1.0.0`
sin cota superior, así que uv instala MCP 2.x, donde `FastMCP` fue renombrado a
`MCPServer` y `mcp.server.fastmcp` ya no existe. Sin el pin, **no arrancan**.
Ninguna de las dos documentaciones upstream lo menciona.

**En Windows, la ruta a `uvx.exe` debe ser absoluta**
(`C:\Users\<tu-usuario>\.local\bin\uvx.exe`). Verificado: con un `PATH` mínimo,
como el que heredan los clientes GUI lanzados desde el menú Inicio, `uvx` da
`NOT FOUND`.

---

## Variables de entorno

Copia `.env.example` a `.env` y rellénalo. **`.env` nunca se commitea.**

---

## Fases

| Fase | Tema | Estado |
|---|---|---|
| 1 | Fundamentos de MCP — `list_tools()` → `call_tool()` | ⬜ |
| 2 | Tu primer MCP server — el protocolo desde dentro | ⬜ |
| 3 | Orquestación con LangGraph — estado y routing | ⬜ |
| 4 | Memoria persistente y comparación con CrewAI | ⬜ |

Detalle en [`PLAN.md`](PLAN.md) y checklist en [`TASKS.md`](TASKS.md).

---

## Referencias

Verificadas durante la planificación:

- Farhi, Goldstone & Gutmann, *A Quantum Approximate Optimization Algorithm*,
  arXiv:1411.4028 (2014)
- Buonaiuto et al., *Best practices for portfolio optimization by quantum
  computing*, Sci. Rep. **13**, 4096 (2023)
- Brandhofer et al., *Benchmarking the performance of portfolio optimization with
  QAOA*, Quantum Inf. Process. **22**, 25 (2022)
- Certo, Pham & Beaulieu, arXiv:2203.04912 (2022)
- Stopfer & Wagner, *Quantum Portfolio Optimization: An Extensive Benchmark*,
  arXiv:2509.17876 (2025)
- Rebentrost & Lloyd, *Quantum Computational Finance*, KI **38**, 327 (2024)

---

## Licencia

MIT. Ver [`LICENSE`](LICENSE).