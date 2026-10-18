# Fase 3 — Orquestación con LangGraph

## 📖 Lee antes de empezar

| Notebook | Qué te da |
|---|---|
| [`theory/langgraph.md`](../../theory/langgraph.md) | Estado, nodos, edges, **reducers**, routing condicional, checkpointer |
| [`theory/agents-concepts.md`](../../theory/agents-concepts.md) | Qué es un agente, ReAct, tool calling |
| [`theory/mcp-agents.md`](../../theory/mcp-agents.md) | Patrón supervisor/router, por qué un agente ≠ una llamada |
| [`theory/qaoa.md`](../../theory/qaoa.md) | **El corazón físico**: Ising → Hamiltoniano, y §9 por qué no hay ventaja |

> **Orden físico obligatorio:** `quantum-physics.md` → `portfolio-math.md` →
> `qaoa.md`. El nodo cuántico no tiene sentido sin el mapeo Markowitz → QUBO.

---

## Objetivo de aprendizaje

Gestionar el estado entre agentes, decidir dinámicamente el siguiente paso, y
depurar flujos multi-paso. Entender **por qué existen los reducers**.

---

## El grafo

```
START
  │
  ▼
analizar_activos ──────► [conditional: alta_volatilidad?]
  │                            │
  │          True              │            False
  │            │               │              │
  │            ▼               │              ▼
  │   optimizacion_robusta    │      analisis_clasico
  │        (QAOA)             │        (Markowitz)
  │            │               │              │
  │            └───────┬───────┘              │
  │                    ▼                      │
  │          generar_recomendacion ◄──────────┘
  │                    │
  └────────────────────►▼
                       END
```

---

## Tareas

### 3.A — Cliente MCP multi-servidor
- [ ] 3.1 `src/.../mcp_clients/session_group.py`: wrapper sobre
      `ClientSessionGroup` leyendo `config/mcp_servers.json`
- [ ] 3.2 `list_all_tools()` fusionando ambos servidores, con prefijo por
      servidor para evitar colisiones
- [ ] 3.3 **Test:** los nombres son únicos tras el prefijo
- [ ] 3.4 Comprobar `is_error=True` con una tool inexistente (**no lanza excepción**)
- [ ] 3.5 Comprobar que `structured_content` envuelve escalares en `{"result": N}`

### 3.B — Grafo lineal
- [ ] 3.6 `state.py` con `TypedDict` (no Pydantic)
- [ ] 3.7 Nodo `analizar_activos`: `scan_universe` + `get_momentum`
- [ ] 3.8 Nodo `simular_qaoa`: **QUBO a mano con numpy** (qiskit-optimization
      está descontinuado), ejecución con **Qiskit directo**
- [ ] 3.9 Nodo `generar_recomendacion`
- [ ] 3.10 Grafo lineal end-to-end
- [ ] 3.11 Guardar el output en `outputs/`

### 3.C — Routing condicional
- [ ] 3.12 `add_conditional_edges` con `path_map`
- [ ] 3.13 Verificar que el **mismo** universo produce **dos rutas distintas**
- [ ] 3.14 **🔴 El reducer**: el dict del circuito debe sobrevivir entre nodos.
      `Annotated[dict, merge_circuit]`. Entender **por qué** hace falta, no
      solo escribirlo
- [ ] 3.15 Checkpointer `AsyncSqliteSaver` + `thread_id`
- [ ] 3.16 Verificar persistencia con `aget_state_history()`
- [ ] 3.17 🔴 Depurar un fallo de estado **a propósito** y anotarlo en
      [`../../docs/learning-log.md`](../../docs/learning-log.md)
- [ ] 3.18 Cerrar la fase y promover a `src/`

---

## 🔴 El momento pedagógico central

**Tarea 3.14.** El servidor `mcp-qiskit` es **stateless**: el circuito es un dict
que hay que reenviar en cada llamada. En un grafo, eso significa que el estado
tiene que *acumularse* entre nodos en vez de sobrescribirse.

Hasta aquí el estado era "el último valor que escribió el nodo". A partir de
aquí es "todos los valores que escribieron los nodos". **Esa es exactamente la
función de un reducer**, y se entiende solo si sufriste el problema en 1.12.

```python
Annotated[dict[str, Any], lambda a, b: b or a]   # el últimoCircuit gana
```

---

## 🔴 Depurar el flujo multi-paso

**Tarea 3.17.** Rompe el estado a propósito (borra un campo, devuelve un tipo
incorrecto) y traza dónde se rompe. Sin esto, depurar un grafo de 5 nodos es
ir a ciegas.

Herramientas que te van a hacer falta:

```python
graph.aget_state_history(config)   # historial completo de pasos
state = await graph.aget_state(config)   # estado actual
```

Ejecuta `simular_qaoa` con un QUBO de 15 qubits y observa cuánto tarda. Es tu
primer aviso de por qué el Hamiltoniano *all-to-all* es un problema (§9 de
`qaoa.md`).

---

## Notas de la API (verificadas)

- `StateGraph`, `START`, `END`, `add_node`, `add_conditional_edges`,
  `compile(checkpointer=...)`: intactos.
- `AsyncSqliteSaver.from_conn_string()` es un **async context manager**:
  envuélvelo en `async with`.
- Necesitas `config={"configurable": {"thread_id": ...}}` en cada invoke.
- Novedades útiles: `add_node(timeout=...)`, `error_handler=(state, error) -> Command`,
  `context_schema=`.
- `langchain-mcp-adapters` está **archivado**. El cliente es propio
  (`decisions.md` AD-0005/AD-0006).

---

## ✅ Criterio de cierre

Dos rutas distintas desde el **mismo** input, y el estado persiste entre
invocaciones con el mismo `thread_id`.

## Convenciones

Cuaderno, pero con tests. Al cerrar, se promueve a `src/` con los reducers,
el cliente multi-servidor y los nodos bien limpios.