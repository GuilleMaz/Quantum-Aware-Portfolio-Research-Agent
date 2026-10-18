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

# Memoria de agentes

> **Prerrequisitos:** `langgraph.md`. **Objetivo:** decidir qué merece
> recordarse de una cartera entre sesiones y cómo representarlo.

## 1. Corta vs larga

- **Corta:** el estado del grafo + el checkpointer (`thread_id`). Muere con la
  sesión o vive en SQLite local.
- **Larga:** conclusiones entre sesiones ("AAPL superó el filtro 3 veces; la
  última QAOA dio estos pesos"). Vive en un servidor de memoria vía MCP.

La pregunta no es cómo guardar, sino **qué** guardar. Guardarlo todo es ruido;
no guardar nada es amnesia.

## 2. Qué merece recordarse de una cartera

```{code-cell} ipython3
# Ejemplo de hecho que sí merece persistir (estructurado, citable).
hecho = {
    "tipo": "conclusion_cartera",
    "universo": ["AAPL", "MSFT", "NVDA"],
    "estrategia": "qaoa",
    "p": 2,
    "pesos": {"AAPL": 0.5, "MSFT": 0.3, "NVDA": 0.2},
    "sharpe_in_sample": 1.2,
    "advertencia": "in-sample; no es recomendación",
}
print(hecho)
```

Merece: universo usado, estrategia, parámetros, resultado y su advertencia. No
merece: precios intermedios, trazas de depuración, histogramas crudos.

## 3. Representaciones

Embeddings (búsqueda por similitud), resúmenes (compresión con pérdida) y hechos
estructurados (precisos, citables). Para carteras: hechos estructurados primero,
embeddings para recuperar sesiones parecidas.

## 4. Decisión de este proyecto

`mcp-memory-service` (self-hosted) en vez de `mem0-mcp-server` (repo
archivado). Ver `decisions.md` AD-0009. El orquestador consulta al inicio y
escribe al final (Fase 4).

## Ejercicios

<details><summary>1. ¿Por qué no guardar los precios en la memoria?</summary>
Porque son datos, no conclusiones: se re-consultan al servidor financiero. La
memoria guarda decisiones y su contexto, no el mercado.
</details>

## Referencias

- Docs de mem0 y de `mcp-memory-service` en PyPI (verificadas existencia;
  sintaxis de auth cloud NO VERIFICADA)
