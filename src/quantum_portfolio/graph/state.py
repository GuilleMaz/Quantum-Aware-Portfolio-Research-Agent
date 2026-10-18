"""Grafo de orquestacion (LangGraph).

Se implementa en la **Fase 3**. Aqui solo queda el esquema del estado y el
mapa de nodos, fijados contra la API real de LangGraph 1.2 verificada.

## Nodos

```
START
  |
  v
analizar_activos -----> [conditional]
  |                          |
  |            alta vol      |    baja vol
  |              |           |       |
  |              v           |       v
  |      optimizacion_robusta |  analisis_clasico
  |        (QAOA)            |    (Markowitz)
  |              |           |       |
  |              +-----+-----+       |
  |                    v             |
  |          generar_recomendacion <+
  |                    |
  +-------------------->+
                       v
                      END
```

## Estado

``TypedDict``, NO Pydantic (decisions.md AD-0007). La documentacion de LangGraph
v1 recomienda ``TypedDict``; Pydantic como estado solo valida en la entrada del
primer nodo y devuelve dicts.

## El reducer: por que hace falta

El Agente Investigador Cuantico devuelve un dict de circuito cuantico que debe
sobrevivir entre nodos. Esa necesidad es lo que justifica
``Annotated[dict, merge_circuit]``. No lo introduzcas antes de necesitarlo.

## Notas de LangGraph 1.2 (verificadas)

- ``StateGraph``, ``START``, ``END``, ``add_node``, ``add_conditional_edges``,
  ``compile(checkpointer=...)``: todo intacto.
- ``AsyncSqliteSaver.from_conn_string(...)`` es un async context manager: hay
  que envolverlo en ``async with``.
- Se necesita ``config={"configurable": {"thread_id": ...}}`` en cada invoke.
- Novedades utiles: ``add_node(timeout=...)``, ``error_handler=(state, error)
  -> Command``, ``context_schema=`` sustituye a la config mutable.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

#: Reducer por defecto para acumular valores en una lista entre nodos.
AppendList = Annotated[list[Any], operator.add]


class PortfolioState(TypedDict, total=False):
    """Estado compartido del grafo de orquestacion.

    Se implementa en la Fase 3. Los campos ya estan fijados porque determinan
    la forma del grafo.
    """

    # --- Entrada ---
    #: Universo de candidatos. Viene de ``config/``, NO del servidor MCP
    #: (que no tiene ninguna tool que devuelva un universo).
    universo: list[str]

    # --- Salida del Analista ---
    #: Activos con metricas de riesgo/retorno.
    metricas: dict[str, Any]
    #: Volatilidad media del universo. Decide el routing.
    volatilidad_media: float
    #: True si supera el umbral de ``config/``. Clave del routing condicional.
    alta_volatilidad: bool

    # --- Estado cuantico entre nodos (justifica el reducer) ---
    #: Dict del circuito cuantico tal y como lo devuelve ``mcp-qiskit``.
    #: Es STATELESS: hay que reenviarlo en cada tool call.
    circuito: Annotated[dict[str, Any], lambda a, b: b or a]

    # --- Salida ---
    #: Pesos de la cartera optimizada.
    pesos: dict[str, float]
    #: Tipo de optimizacion que se ejecuto: "qaoa" | "markowitz" | "error".
    estrategia: str
    recomendacion: str

    #: Traza de ejecucion para depurar el flujo multi-paso.
    pasos: AppendList


__all__ = ["AppendList", "PortfolioState"]