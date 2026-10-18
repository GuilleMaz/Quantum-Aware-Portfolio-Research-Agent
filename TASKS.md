# TASKS.md — Checklist ejecutable

**Regla:** una tarea marcada = un commit (`AGENTS.md` §5).

**Al terminar cada tarea:**
1. Marca la casilla.
2. Actualiza `project-memory/changelog.md` (entrada nueva arriba).
3. Actualiza `project-memory/next-steps.md`.
4. Si hubo decisión de diseño → `project-memory/decisions.md`.
5. Commit.

---

## Fase 0 — Estructura del repo

- [x] **0.1** `git init`, rama `main`, remoto `origin` apuntando a GitHub
- [x] **0.2** `pyproject.toml` con grupos de dependencias + `ruff`/`mypy`/`pytest`
- [x] **0.3** `.gitignore` (regla crítica: `.env` fuera) y `.gitattributes`
- [x] **0.4** `.python-version` = 3.12, `LICENSE` MIT con disclaimer
- [x] **0.5** Árbol de directorios completo
- [x] **0.6** `README.md` con aviso honesto sobre ventaja cuántica
- [x] **0.7** `AGENTS.md` — el contrato de trabajo
- [x] **0.8** `PLAN.md` — roadmap de las 4 fases
- [x] **0.9** `TASKS.md` — este fichero
- [x] **0.10** `project-memory/` con los 5 archivos y contenido real
- [x] **0.11** `docs/` (4 ficheros + `adr/`) y `config/` (`mcp_servers.json`)
- [x] **0.12** `theory/` — 13 notebooks MyST
- [x] **0.13** `labs/` — 4 carpetas de fase con README que enlazan a `theory/`
- [x] **0.14** `src/quantum_portfolio/` — estructura vacía
- [x] **0.15** `.env.example`
- [x] **0.16** `opencode.json` + `config/clients/*.example.json` (3 clientes)
- [x] **0.17** Push a GitHub

---

## Fase 1 — Fundamentos de MCP

> 📖 Lee antes: [`theory/mcp.md.ipynb`](theory/mcp.md.ipynb),
> [`theory/tool-discovery.md.ipynb`](theory/tool-discovery.md.ipynb),
> [`theory/qiskit-basics.md.ipynb`](theory/qiskit-basics.md.ipynb)

### 1.A — Servidor financiero

- [ ] **1.1** `uv sync` y comprobar que el venv arranca
- [ ] **1.2** Lanzar el server y hacer el handshake `initialize` a mano
      (`uvx --from financial-mcp-server --with "mcp<2" financial-mcp`)
- [ ] **1.3** `list_tools.py`: listar las 42 herramientas → `snapshots/financial_tools.json`
- [ ] **1.4** `call_tool.py`: `get_price("AAPL")` → guardar salida real
- [ ] **1.5** `call_tool.py`: `get_fundamentals("AAPL")` → guardar salida real
- [ ] **1.6** `call_tool.py`: `get_momentum("AAPL")` → **trae la volatilidad** →
      guardar
- [ ] **1.7** Leer y parsear el `{"result": "<json string>"}` que devuelve.
      Anotar el problema del doble encoding en `docs/mcp-notes.md`

### 1.B — Servidor cuántico

- [ ] **1.8** Lanzar `uvx --from "mcp-qiskit[mcp]" mcp-qiskit`. **Paciencia: 67 s**
- [ ] **1.9** `list_tools()` → las 13 herramientas → `snapshots/qiskit_tools.json`
- [ ] **1.10** `bell_circuit.py`: `create` → `add_gate(h)` → `add_gate(cx)` →
      `add_measurement` → `run(shots=1024)`
- [ ] **1.11** Verificar `{"00": ~512, "11": ~512, "01": ~0, "10": ~0}` →
      `snapshots/bell_circuit.json`
- [ ] **1.12** **Descubrir que es stateless**: olvidar reenviar el dict del
      circuito en el segundo `add_gate` y observar qué pasa. Anotar en
      `docs/mcp-notes.md`. **Esta es la tarea más importante de la fase.**
- [ ] **1.13** Probar el fallo silencioso: `rx` sin `params` y comprobar que el
      circuito queda mal sin error. Anotarlo.
- [ ] **1.14** `draw_circuit_tool("ascii")` con `PYTHONIOENCODING=utf-8`

### 1.C — Integración con el LLM

- [ ] **1.15** Copiar `config/clients/claude_desktop_config.example.json` a
      `%APPDATA%\Claude\claude_desktop_config.json` (con ruta absoluta a `uvx.exe`)
- [ ] **1.16** Conectar en OpenCode vía `opencode.json`, confirmar con `/mcps`
      que los 3 servidores aparecen
- [ ] **1.17** Pedirle al LLM un análisis de ticker **sin nombrar las
      herramientas**. Comprobar que las elige bien.
- [ ] **1.18** Pedirle un circuito de Bell. Ver si recuerda reenviar el circuito.
- [ ] **1.19** Cerrar la fase: promover lo reusable a `src/`, actualizar
      `project-memory/`

**✅ Criterio de cierre:** `snapshots/bell_circuit.json` con distribución Bell
correcta ±5%.

---

## Fase 2 — Tu primer MCP server

> 📖 Lee antes: [`theory/python-sdk.md.ipynb`](theory/python-sdk.md.ipynb),
> [`theory/mcp.md.ipynb`](theory/mcp.md.ipynb)

- [ ] **2.1** Crear `labs/phase2-own-server/` con `pyproject.toml`
- [ ] **2.2** `compound_interest(principal, rate, periods)` con anotaciones de
      tipo. Comprobar que el tipo **es** el JSON Schema.
- [ ] **2.3** `loan_emi(principal, annual_rate, years)` con amortización francesa
- [ ] **2.4** `npv(rate, cashflows)` 
- [ ] **2.5** Tests unitarios de las tres funciones (casos límite: 0 años, tasa 0)
- [ ] **2.6** `uv run mcp dev server.py` y abrir MCP Inspector
- [ ] **2.7** Conectar a OpenCode
- [ ] **2.8** **Prueba de diseño de contrato**: pedir "cuánto pago al mes por un
      coche de 20.000€ al 8% a 5 años". El LLM debe elegir `loan_emi` **sin que
      le digas el nombre**. Si hay que nombrarla, reescribe la descripción.
- [ ] **2.9** Comparar `list_tools()` de tu server con el del financiero.
      Anotar en `docs/mcp-notes.md` qué hacen las descripciones buenas.
- [ ] **2.10** Cerrar la fase y promover a `src/`

**✅ Criterio de cierre:** el LLM elige la herramienta correcta sin ayuda.

---

## Fase 3 — Orquestación con LangGraph

> 📖 Lee antes: [`theory/langgraph.md.ipynb`](theory/langgraph.md.ipynb),
> [`theory/agents-concepts.md.ipynb`](theory/agents-concepts.md.ipynb),
> [`theory/mcp-agents.md.ipynb`](theory/mcp-agents.md.ipynb),
> [`theory/qaoa.md.ipynb`](theory/qaoa.md.ipynb)

### 3.A — Cliente MCP multi-servidor

- [ ] **3.1** `src/quantum_portfolio/mcp_clients/session_group.py`: wrapper sobre
      `ClientSessionGroup` con los servidores de `config/mcp_servers.json`
- [ ] **3.2** `list_all_tools()` fusionando los 2 servidores, con prefijo por
      servidor para evitar colisiones de nombres
- [ ] **3.3** Test: los nombres son únicos tras el prefijo
- [ ] **3.4** Comprobar `is_error=True` en un tool inexistente (no lanza excepción)
- [ ] **3.5** Comprobar que `structured_content` envuelve escalares en `{'result': N}`

### 3.B — Grafo lineal

- [ ] **3.6** `state.py` con `TypedDict` (no Pydantic — ver `decisions.md`)
- [ ] **3.7** Nodo `analizar_activos`: llama a `scan_universe` + `get_momentum`
- [ ] **3.8** Nodo `simular_qaoa`: construye el QUBO con numpy (**no**
      `qiskit-optimization`, descontinuado), usa Qiskit directo
- [ ] **3.9** Nodo `generar_recomendacion`
- [ ] **3.10** Grafo lineal funcionando end-to-end
- [ ] **3.11** Guardar el output en `outputs/`

### 3.C — Routing condicional

- [ ] **3.12** `add_conditional_edges` con `path_map`: alta volatilidad →
      `optimizacion_robusta` (QAOA), si no → `analisis_clasico` (Markowitz)
- [ ] **3.13** Verificar que el **mismo** universo produce dos rutas distintas
- [ ] **3.14** **El reducer**: el dict del circuito debe sobrevivir entre nodos.
      `Annotated[dict, merge_circuit]`. Entiende **por qué** hace falta.
- [ ] **3.15** Checkpointer `AsyncSqliteSaver` + `thread_id`
- [ ] **3.16** Verificar persistencia con `aget_state_history()`
- [ ] **3.17** Depurar un fallo de estado a propósito (`config/../tests/`) y
      anotarlo en `docs/learning-log.md`
- [ ] **3.18** Cerrar la fase y promover a `src/`

**✅ Criterio de cierre:** dos rutas distintas desde el mismo input, y el estado
persiste entre invocaciones con el mismo `thread_id`.

---

## Fase 4 — Memoria y comparación con CrewAI

> 📖 Lee antes: [`theory/agent-memory.md.ipynb`](theory/agent-memory.md.ipynb)

- [ ] **4.1** Levantar `mcp-memory-service` (`uvx --from mcp-memory-service
      memory server`)
- [ ] **4.2** `src/quantum_portfolio/agents/memory.py`: guardar y recuperar
      conclusiones de carteras anteriores
- [ ] **4.3** El orquestador consulta la memoria al inicio y escribe al final
- [ ] **4.4** Verificar: el sistema recuerda una cartera de una sesión anterior
- [ ] **4.5** `labs/phase4-memory-crewai/`: el **mismo grafo** en CrewAI
- [ ] **4.6** Tabla comparativa LangGraph vs CrewAI → `decisions.md`
- [ ] **4.7** Cerrar la fase

**✅ Criterio de cierre:** tabla comparativa escrita y justificada.

---

## Backlog

### Papers por verificar

- [ ] Buscar el estado real de los papers de portfolio cuántico post-2025.
      Las citas de `theory/qaoa.md.ipynb` §9 están verificadas a 2026-10-18;
      esta tarea es mantenerlas al día.

### Mejoras de robustez

- [ ] `mcp-qiskit` devuelve `statevector` como strings → wrapper que parsea.
      Mientras tanto, usar Qiskit directo (`AGENTS.md` §8).
- [ ] Cachear salidas de `get_price_history` en `data/` (rate limits de Yahoo).
- [ ] Guardarraíl contra los gates paramétricos sin `params` (fallo silencioso).

### Cosas pendientes de verificar

- [ ] Sin embargo oficial de `mcp-intro` (el tutorial citado en el plan
      original **no existe como repo**). Sustituido por los ejemplos oficiales
      de LangGraph + la spec MCP.
- [ ] `mcp-memory-service` vs la alternativa cloud `https://mcp.mem0.ai/mcp`.
      La sintaxis del header de auth no está verificada.

---

## Notas de progreso

*(Bitácora breve. El detalle va en `project-memory/changelog.md`.)*

- **2026-10-18** — Fase 0 completa: repo inicializado, 4 archivos raíz,
  `project-memory/`, `docs/`, `config/`, 13 notebooks en `theory/`,
  4 carpetas en `labs/`, estructura de `src/`, configs de 3 clientes. Push.