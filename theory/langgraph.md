---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
kernelspec:
  display_name: Python 3
  name: python3
---

# LangGraph — grafos de estado

> **Prerrequisitos:** `agents-concepts.md`. **Objetivo:** estado con
> `TypedDict`, nodos, aristas condicionales, reducers y checkpointer. Todo
> verificado contra LangGraph 1.2.

## 1. El grafo mínimo

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)          # State es un TypedDict
builder.add_node("analizar", analizar)
builder.add_node("simular", simular)
builder.add_edge(START, "analizar")
builder.add_conditional_edges("analizar", ruta_por_volatilidad, {...})
graph = builder.compile(checkpointer=checkpointer)
```

`StateGraph` + `add_node` + `add_conditional_edges` + `compile()`: todo intacto
en la v1.2.

## 2. Estado: TypedDict, no Pydantic

```{code-cell} ipython3
import operator
from typing import Annotated, TypedDict

class Estado(TypedDict, total=False):
    universo: list
    alta_volatilidad: bool
    pasos: Annotated[list, operator.add]  # reducer: acumula entre nodos

print(Estado.__annotations__.keys())
```

La documentación recomienda `TypedDict`. Pydantic como estado solo valida en la
entrada del primer nodo, devuelve dicts (no instancias) y coacciona tipos en
silencio (`"42"` → `42`). Pydantic queda para los datos (`Asset`, `Metrics`).

## 3. Reducers: por qué existen

Sin reducer, cada nodo **sobrescribe** el campo. Con reducer, se **combina**.
El caso real de este proyecto: el dict del circuito cuántico debe sobrevivir
entre nodos porque `mcp-qiskit` es stateless y hay que reenviarlo en cada
llamada. `Annotated[dict, merge]` es la diferencia entre "el último valor gana"
y "el estado se acumula". Se entiende en la Fase 3, tarea 3.14, sufriéndolo.

## 4. Routing condicional

```python
builder.add_conditional_edges(
    "analizar",
    lambda s: "robusta" if s["alta_volatilidad"] else "clasica",
    {"robusta": "optimizacion_robusta", "clasica": "analisis_clasico"},
)
```

El `path_map` traduce el string que devuelve la función al nombre del nodo.
El mismo universo produce dos rutas distintas según la volatilidad: ese es el
criterio de éxito de la Fase 3.

## 5. Persistencia

```python
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as cp:
    graph = builder.compile(checkpointer=cp)
    await graph.ainvoke(estado, {"configurable": {"thread_id": "t1"}})
```

`from_conn_string` es un **async context manager** y cada invocación necesita
su `thread_id`. El historial se inspecciona con `aget_state_history()`: es la
herramienta de depuración del flujo multi-paso.

## 6. ToolNode

`langgraph.prebuilt.ToolNode` ejecuta herramientas y `tools_condition` decide
si seguir llamando o terminar. Acepta cualquier `BaseTool`, incluidas las
construidas a mano desde `Client.list_tools()`.

## Ejercicios

<details><summary>1. ¿Cuándo necesitas un reducer?</summary>
Cuando dos nodos escriben el mismo campo y quieres conservar ambos (listas,
dicts de circuito) en vez de que el último pise al anterior.
</details>

<details><summary>2. ¿Qué pasa si dos invocaciones comparten thread_id?</summary>
El estado persiste entre ellas: la segunda ve lo que dejó la primera. Es la
base de la memoria de sesión.
</details>

## Referencias

- Docs de LangGraph: https://langchain-ai.github.io/langgraph/ (verificada)
