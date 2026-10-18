# Fase 4 — Memoria persistente y comparación con CrewAI

## 📖 Lee antes de empezar

| Notebook | Qué te da |
|---|---|
| [`theory/agent-memory.md`](../../theory/agent-memory.md) | Memoria corta vs larga, embeddings, qué merece recordarse |
| [`theory/langgraph.md`](../../theory/langgraph.md) | Repaso del modelo de grafo, para comparar con conocimiento |

> Depende de cerrar la Fase 3. El sistema ya orquesta dos agentes con estado;
> aquí se le da memoria entre sesiones y se reimplementa con otro framework
> para comparar.

---

## Objetivo de aprendizaje

Dos cosas distintas:

1. **Qué merece recordarse** de una cartera entre sesiones (y qué no), y cómo
   se representa: embeddings, resúmenes, hechos estructurados.
2. **Las diferencias reales** entre el modelo de "grafo de estado" (LangGraph)
   y el de "roles y tareas" (CrewAI), medidas sobre el **mismo** problema.

---

## Tareas

### 4.A — Memoria
- [ ] 4.1 Levantar `mcp-memory-service`:
      `uvx --from mcp-memory-service memory server`
- [ ] 4.2 `src/.../agents/memory.py`: guardar y recuperar conclusiones de
      carteras anteriores
- [ ] 4.3 El orquestador consulta la memoria al inicio del ciclo y escribe al
      final
- [ ] 4.4 Verificar: el sistema recuerda una cartera de una sesión anterior
      (misma pregunta, respuesta que cita la sesión previa)

### 4.B — Comparación con CrewAI
- [ ] 4.5 `labs/phase4-memory-crewai/crewai_comparison/`: el **mismo grafo**
      reescrito en CrewAI (mismos nodos, mismas herramientas)
- [ ] 4.6 Tabla comparativa → `project-memory/decisions.md` con, como mínimo:
      tiempo de desarrollo, control del flujo, testeabilidad, coste en tokens,
      y qué modelo se ajusta mejor a este problema
- [ ] 4.7 Cerrar la fase y promover a `src/`

---

## 🟡 La decisión ya tomada (y por qué se revisa al llegar)

`mem0-mcp-server` era el candidato del plan original. Investigación posterior:

- `mem0-mcp` **no existe en PyPI** (404).
- `mem0-mcp-server` 0.2.1 funciona, pero su repo `mem0ai/mem0-mcp` está
  **archivado** y arrastra ~89 paquetes.
- `mcp-memory-service` es self-hosted, sin cloud, verificado funcional.

Por eso la tarea 4.1 usa `mcp-memory-service`. Si falla en tu máquina, **es un
excelente ejercicio de diagnóstico**: tienes la Fase 2 para escribir tu propio
servidor de memoria si hace falta (plan B documentado en `decisions.md` AD-0009).

---

## ✅ Criterio de cierre

Tabla comparativa LangGraph vs CrewAI escrita y justificada en `decisions.md`.

## Convenciones

Cuaderno. Al cerrar, la memoria persistente se promueve a `src/` y la
comparación queda como documentación permanente.
