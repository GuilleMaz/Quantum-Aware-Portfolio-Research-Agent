# PLAN.md — Roadmap

Roadmap de las 4 fases del proyecto. Cada fase tiene un **objetivo de
aprendizaje**, un **entregable verificable** y una lista explícita de lo que
**no** incluye.

**El estado de avance vive en [`TASKS.md`](TASKS.md). El estado del proyecto
vive en [`project-memory/`](project-memory/). Este fichero no se actualiza
tarea a tarea, sino al cerrar o ajustar una fase.**

---

## Mapa de las fases

```
Fase 1 ──────► Fase 2 ──────► Fase 3 ──────► Fase 4
MCP como        MCP desde      Orquestación    Memoria y
consumidor       dentro        con estado      comparación
```

Las fases son **secuenciales a propósito**. Cada una existe para que la
siguiente sea obvia. Saltarse la 2 y escribir el servidor propio en la 3
significa no entender nunca por qué `list_tools()` funciona.

---

## Fase 1 — Fundamentos de MCP

**Objetivo de aprendizaje**
Entender el ciclo `list_tools()` → `call_tool()` y que MCP estandariza la
interfaz. Ver que un servidor MCP es **un proceso separado** que anuncia
capacidades, y que las descripciones de las herramientas son **contratos para
el LLM**, no documentación decorativa.

**Entregable**
`labs/phase1-mcp-basics/` con:
- Catálogo real de las 42 herramientas del servidor financiero, guardado en
  `snapshots/financial_tools.json`.
- Dos llamadas reales a herramientas de precio y fundamentales, con salida
  guardada.
- Circuito de Bell ejecutado en `aer_simulator` vía `mcp-qiskit`, distribución
  guardada en `snapshots/bell_circuit.json`.
- Los tres servidores conectados a OpenCode y el LLM usándolos en conversación.

**Criterio de éxito (verificable)**
```json
// snapshots/bell_circuit.json
{ "counts": { "00": 522, "11": 502 }, "shots": 1024 }
```
Distribución de Bell correcta: `00` y `11` con ~50% cada uno, `01` y `10` con
~0%. Tolerancia ±5%.

**No incluye**
Ningún agente. Ningún grafo. Ninguna lógica reutilizable.

**Trampa central de esta fase**
`mcp-qiskit` es **stateless**: hay que reenviar el dict del circuito en cada
llamada. Se descubre aquí, Sufriéndolo, y por eso el reducer de LangGraph de la
Fase 3 tiene sentido cuando aparezca.

---

## Fase 2 — Tu primer MCP server

**Objetivo de aprendizaje**
Comprender que un MCP server es un proceso separado, que escribe sus
capacidades al arrancar, y que la **descripción de una herramienta es lo único
que el LLM tiene para decidir si la usa**. Escribirla bien no es documentación,
es diseño de interfaz.

**Entregable**
Un servidor MCP propio de finanzas con 3 herramientas:
- `compound_interest` — capital final dado principal, tasa y periodos.
- `loan_emi` — cuota de un préstamo con amortización francesa.
- `npv` — valor presente de un flujo de caja.

Con su `pyproject.toml`, tests, y conectado a OpenCode verificando que el LLM
lo invoca **sin que se lo pidamos por nombre**.

**Criterio de éxito**
El LLM elige `loan_emi` cuando le pides "cuánto pago al mes por un coche de
20.000€ al 8% a 5 años" — sin mencionar la herramienta. Si hay que decirle el
nombre, la descripción está mal.

**No incluye**
Acceso a datos reales. La idea es entender el protocolo, no construir un
producto.

**Usa MCP SDK v2**: `from mcp.server import MCPServer` + `@mcp.tool()`.
Escribe las anotaciones de tipo: `a: int, b: int` **es** el JSON Schema. El
docstring **es** el contrato.

---

## Fase 3 — Orquestación con LangGraph

**Objetivo de aprendizaje**
Gestionar el estado entre agentes, decidir dinámicamente el siguiente paso, y
depurar flujos multi-paso. Entender **por qué existen los reducers**.

**Entregable**
`labs/phase3-langgraph/` con dos grafos, en orden:
1. **Lineal**: `analizar_activos` → `simular` → `recomendacion`.
2. **Condicional**: si el analista detecta alta volatilidad, el orquestador
   deriva a `optimizacion_robusta` (QAOA); si no, a `analisis_clasico`
   (Markowitz).

Conectados a **dos servidores MCP simultáneos** mediante `ClientSessionGroup`,
con checkpointer SQLite y `thread_id` para persistencia.

**Criterio de éxito**
El mismo universo de activos produce dos rutas distintas del grafo según la
volatilidad detectada, y el estado persiste entre invocaciones con el mismo
`thread_id`. Verificado con `aget_state_history()`.

**No incluye**
CrewAI (eso es Fase 4). Memoria a largo plazo (también Fase 4).

**El momento pedagógico clave**
El agente cuántico devuelve un dict de circuito que debe sobrevivir entre
nodos. Esa necesidad es la que justifica `Annotated[dict, reducer]`. No lo
introduzcas antes de necesitarla.

---

## Fase 4 — Memoria y comparación

**Objetivo de aprendizaje**
Qué merece recordarse de una cartera entre sesiones, y las diferencias reales
entre el modelo de "grafo de estado" (LangGraph) y el de "roles y tareas"
(CrewAI).

**Entregable**
- Memoria persistente con un servidor MCP de memoria, de modo que el sistema
  recuerde carteras anteriores y sus conclusiones.
- Una implementación equivalente en CrewAI, **con el mismo grafo de nodos**, para
  comparar lado a lado.

**Criterio de éxito**
Una tabla comparativa escrita a mano en `project-memory/decisions.md` con:
tiempo de desarrollo, control del flujo, testeabilidad, coste en tokens,
y qué modelo se ajusta mejor a este problema.

**No incluye**
Ningún cambio al motor cuántico. Ninguna optimización de rendimiento.

**Decisión ya tomada**
`mem0-mcp-server` (el repo de GitHub está **archivado**) → usar
`mcp-memory-service`, que es self-hosted y no depende de la nube. Confirmar al
llegar; si falla, es un excelente ejercicio de diagnóstico.

---

## Orden de lectura de `theory/`

Los notebooks son **transversales**, no están atados a una fase. Ruta:

```
1. theory/index.md          Ruta de lectura y glosario
2. theory/mcp.md            El protocolo            ┐
3. theory/tool-discovery.md Cómo elige el LLM       ├ Fase 1-2
4. theory/python-sdk.md     Escribir un server      ┘
5. theory/agents-concepts.md  Qué es un agente      ┐
6. theory/mcp-agents.md     ReAct, tool calling     ├ Fase 3
7. theory/langgraph.md      Estado, nodos, reducers ┘
8. theory/quantum-physics.md   Cimientos            ┐
9. theory/qiskit-basics.md     Compuertas y Aer      ├ Fase 1
10. theory/portfolio-math.md    Sharpe, Markowitz,  │
                                       de Markowitz a QUBO │ Fase 3
11. theory/qaoa.md              QAOA a fondo        ┘
12. theory/agent-memory.md      Memoria de agentes   Fase 4
```

**Orden de lectura físico obligatorio: 8 → 10 → 11.** El Hamiltonian de coste
de `qaoa.md` no tiene sentido sin el mapeo a QUBO de `portfolio-math.md` §7, ni
ese mapeo sin saber qué es un estado entrelazado y una traza parcial.

---

## Reglas transversales

1. **Lee antes de codificar.** Cada `labs/phaseN-*/README.md` enlaza a los
   notebooks de `theory/` que hay que leer antes de empezar esa fase.
2. **Un commit por tarea**, formato en `AGENTS.md` §5.
3. **Promueve de `labs/` a `src/`** al cerrar cada fase.
4. **Actualiza `project-memory/`** tras cada tarea (`AGENTS.md` §4).
5. **Ninguna afirmación sobre ventaja cuántica sin fuente verificable.**