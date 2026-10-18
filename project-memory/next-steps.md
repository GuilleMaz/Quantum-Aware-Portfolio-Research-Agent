# Next Steps

> **Tareas pendientes, bugs conocidos y prioridades.** Actualizar tras cada
> tarea (`AGENTS.md` §4).
> El detalle histórico va en `changelog.md`.

---

## Siguiente acción recomendada

**Leer `theory/index.md.ipynb` y empezar la Fase 1.1.**

```powershell
uv sync
```

Después: `labs/phase1-mcp-basics/README.md` tiene la lista completa.

---

## Alta prioridad — Fase 1

### Antes de codificar
- [ ] Leer `theory/index.md.ipynb` (ruta de lectura + glosario)
- [ ] Leer `theory/mcp.md.ipynb` (el protocolo)
- [ ] Leer `theory/qiskit-basics.md.ipynb` (Qiskit y Aer)
- [ ] `uv sync` y confirmar que el venv arranca

### 1.A — Servidor financiero
- [ ] Handshake `initialize` manual contra
      `uvx --from financial-mcp-server --with "mcp<2" financial-mcp`
- [ ] `list_tools.py` → `snapshots/financial_tools.json` (42 tools)
- [ ] `get_price`, `get_fundamentals`, `get_momentum` → guardar salidas reales
- [ ] **Parsear el doble encoding `{"result": "<json string>"}`** y anotarlo

### 1.B — Servidor cuántico
- [ ] Lanzar `uvx --from "mcp-qiskit[mcp]" mcp-qiskit` — **paciencia: 67 s**
- [ ] `list_tools()` → 13 tools
- [ ] Circuito de Bell end-to-end → `snapshots/bell_circuit.json`
- [ ] **Descubrir que es stateless** (olvidar reenviar el dict, ver qué pasa).
      **La tarea más importante de la fase.**
- [ ] Reproducir el fallo silencioso de `rx` sin `params`

### 1.C — Integración LLM
- [ ] Copiar el config a `%APPDATA%\Claude\claude_desktop_config.json`
      (ruta absoluta a `uvx.exe`)
- [ ] Conectar en OpenCode, verificar con `/mcps`
- [ ] Pedir un análisis de ticker **sin nombrar las herramientas**
- [ ] Cerrar la fase: promover a `src/`, actualizar `project-memory/`

**Criterio de cierre:** `snapshots/bell_circuit.json` con `{"00": ~512,
"11": ~512, "01": ~0, "10": ~0}` ± 5%.

---

## Prioridad media — Fases 2-4

### Fase 2 (depende de cerrar 1)
- [ ] MCP server propio: `compound_interest`, `loan_emi`, `npv`
- [ ] Tests de las tres funciones
- [ ] `uv run mcp dev server.py` + MCP Inspector
- [ ] **Prueba de contrato**: el LLM debe elegir `loan_emi` sin nombrarla

### Fase 3 (depende de cerrar 2)
- [ ] `mcp_clients/session_group.py` sobre `ClientSessionGroup`
- [ ] Tests de colisión de nombres, `is_error`, `structured_content`
- [ ] Grafo lineal: `analizar_activos` → `simular_qaoa` → `recomendacion`
- [ ] Routing condicional por volatilidad
- [ ] **El reducer** para el dict del circuito (`Annotated[dict, merge]`)
- [ ] Checkpointer SQLite + `thread_id`, verificar con `aget_state_history()`
- [ ] Depurar un fallo de estado a propósito y anotarlo

### Fase 4
- [ ] `mcp-memory-service`: guardar/recuperar conclusiones de carteras
- [ ] El mismo grafo en CrewAI, para comparar
- [ ] Tabla comparativa LangGraph vs CrewAI → `decisions.md`

---

## Bugs conocidos (de terceros)

Verificados empíricamente. Detalle en `AGENTS.md` §7 y `docs/mcp-notes.md`.

### Bloqueantes (hay que trabajar alrededor)
| Bug | Workaround |
|---|---|
| `financial-mcp-server` no arranca con MCP 2.x | `--with "mcp<2"` |
| `mcp-qiskit` no arranca sin el extra `mcp` | `--from "mcp-qiskit[mcp]"` |
| `mcp-qiskit` es stateless | Reenviar el dict del circuito en cada llamada |
| Gates paramétricos sin `params` fallan **en silencio** | **Verificar siempre los `params`.** Peligroso. |
| `statevector` viene como strings | Usar Qiskit directo (`AGENTS.md` §8) |
| `run_circuit` degrada en silencio de backend | No confiar en el backend reportado |
| No hay tool de "universo de activos" | El universo vive en nuestro `config/` |

### No bloqueantes
| Bug | Workaround |
|---|---|
| `seed=0` se convierte en `42` | No usar `seed=0` |
| `draw_circuit("ascii")` rompe en cp1252 | `PYTHONIOENCODING=utf-8` |
| `financial-mcp-server` trunca a 250 bars | Dividir el histórico en varias llamadas |
| `structured_content` envuelve escalares en `{"result": N}` | Desenvolver siempre |
| Errores de tool no lanzan excepción | Comprobar `is_error` |
| El hijo MCP no hereda el entorno | Pasar `env=` explícito |
| `langchain-mcp-adapters` archivado | Cliente MCP propio (AD-0005) |
| `qiskit-optimization` descontinuado | QUBO a mano con numpy |
| CI de `mcp-qiskit` nunca ejecutada (rama `master` vs `main`) | Asumir que los tests no cubren nada |

---

## Deuda técnica conocida

- [ ] **Guardarraíl contra gates sin `params`.** Un validador que rechace
      circuits con `rx`/`u3`/`ry` sin `params` sería un gran primer test.
- [ ] **Caché de `get_price_history`.** Yahoo Finance limita por rate; el
      server mitiga con `curl_cffi` + caché de 120 s en proceso, pero se
      pierde al reiniciar. Una caché en `data/` ayudaría.
- [ ] **Wrapper que parsee `statevector` de `mcp-qiskit`.** Solución
      intermedia mientras se usa Qiskit directo.
- [ ] **`src/` no tiene ningún módulo todavía.** Se puebla por promoción desde
      `labs/`. Si necesitas algo antes de la Fase 3, promoting desde `labs/` es
      el camino.

---

## Cosas por verificar

- [ ] **El tutorial `mcp-intro`** citado en el plan original **no existe como
      repo**. Buscar el correcto o confirmar que se usan los ejemplos oficiales
      de LangGraph + la spec MCP.
- [ ] **Sintaxis del header de auth** de `https://mcp.mem0.ai/mcp` (alternativa
      cloud a `mcp-memory-service`).
- [ ] **Estado de los papers de portfolio cuántico post-2025.** Las citas de
      `theory/qaoa.md.ipynb` §9 están verificadas a 2026-10-18.
- [ ] **Si `mcp-memory-service` arranca en Windows.** Verificado el `--help`,
      no el handshake completo.

---

## Mejoras futuras (post-Fase 4)

- [ ] Tests de integración marcados con `@pytest.mark.integration`
- [ ] Human-in-the-loop en el grafo (`interrupt_before` en el nodo de
      recomendación)
- [ ] Comparar QAOA vs Markowitz vs random en la misma instancia,
      visualizándolo en un notebook de `notebooks/`
- [ ] Considerar `retries`/`fault_tolerance` de MCP (`client.connect(...)` con
      reconexión) para servidores tan frágiles como estos dos

---

## Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| `financial-mcp-server` abandonado (4 meses sin commits) | El Agente Analista se queda sin datos | Plan B: `yfinance` directo (es la misma dependencia que ya usa por dentro) |
| `mcp-qiskit` abandonado (5 meses) | La Fase 3 pierde su server cuántico | Plan B: Qiskit directo ya decidido (AD-0008) |
| Los dos externos incompatibles con MCP 2.x | Ya está resuelto | `--with "mcp<2"` (AD-0004) |
| Yahoo Finance limita por rate | Timeouts intermitentes | Caché + `scan_universe` batch en vez de N llamadas |
| Primera ejecución de `mcp-qiskit` tarda 67 s | Timeout si `mcp.timeout` está en default | `timeout: 60000` en los configs |
| Los notebooks de física tienen errores de detalle fino | Contenido incorrecto | El usuario (físico) debe revisarlos — es su contenido nativo |