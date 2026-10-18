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

# Qué es un agente

> **Prerrequisitos:** ninguno. **Objetivo:** fijar qué significa "agente" en este
> repo, y los patrones ReAct, tool calling y supervisor.

## 1. Definición operativa

Un **agente** = un LLM en un bucle con herramientas y memoria:

```
percepción (estado, herramientas disponibles)
  → razonamiento (el modelo decide)
  → acción (llamar una herramienta)
  → observación (el resultado vuelve al contexto)
  → repetir hasta responder o agotar el presupuesto
```

Sin herramientas no hay agente: hay un chatbot. Sin bucle no hay agente: hay
una llamada. Este proyecto tiene dos agentes (Analista e Investigador) más un
orquestador que decide el orden.

## 2. ReAct: razonar + actuar

El patrón clásico (Yao et al. 2022): el modelo intercala trazas de razonamiento
con acciones, y las observaciones corrigen el rumbo.

```
Thought: necesito la volatilidad de AAPL.
Action: get_momentum({"symbol": "AAPL"})
Observation: {"volatility": 0.31, ...}
Thought: 31% es alta; pido el régimen de mercado para contextualizar.
Action: detect_market_regime({})
```

```{code-cell} ipython3
# ReAct en miniatura, sin LLM: el bucle es lo que importa.
def agente_demo(observaciones):
    plan = ["get_momentum", "detect_market_regime", "responder"]
    for paso in plan:
        print(f"Thought: toca {paso}")
        print(f"Action: {paso} -> Observation: {observaciones.get(paso, 'ok')}")

agente_demo({"get_momentum": "vol=0.31", "detect_market_regime": "HIGH_VOLATILITY"})
```

## 3. Tool calling nativo vs ReAct escrito a mano

- **ReAct a mano:** el modelo escribe `Action: ...` como texto y tu código lo
  parsea. Frágil pero transparente.
- **Tool calling nativo:** el proveedor devuelve llamadas estructuradas
  (`bind_tools`). Robusto, pero el modelo decide sin mostrar el "thought".

En LangGraph usarás `bind_tools` + `ToolNode`: el grafo ejecuta la herramienta y
devuelve la observación al modelo. El bucle ReAct vive dentro del grafo.

## 4. Supervisor / router

Con varios agentes hace falta quién decide el siguiente paso. Dos modelos:

- **Grafo de estado** (LangGraph): los nodos son agentes, las aristas deciden.
  El estado es explícito y auditable.
- **Roles y tareas** (CrewAI): cada agente tiene rol, objetivo y herramientas;
  el framework reparte. Menos control, menos código.

La Fase 4 implementa lo mismo en ambos y compara. Adelanto: para un flujo con
routing por volatilidad, el grafo gana en control; para una redacción
colaborativa, los roles son más cómodos.

## Ejercicios

<details><summary>1. ¿Por qué un agente no es una llamada?</summary>
Porque decide la siguiente acción viendo la observación anterior. Una llamada es
un disparo; un agente es un bucle con criterio de parada.
</details>

## Referencias

- ReAct (Yao et al., arXiv:2210.03629, 2022) (verificada)
