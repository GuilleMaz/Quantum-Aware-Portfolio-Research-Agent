# Decisions

> Registro de decisiones técnicas (ADRs resumidos). Los ADRs completos con
> más contexto están en [`../docs/adr/`](../docs/adr/).
> **Agregar nuevas entradas al inicio.**
> Para el "por qué" de las decisiones exploratorias, ver `../PLAN.md`.

---

## 2026-10-18 — AD-0009: `mcp-memory-service` sobre `mem0-mcp-server`

### Problema
Fase 4 necesita un servidor MCP de memoria. El plan original citaba `mem0-mcp`.

### Decisión
Usar `mcp-memory-service` (self-hosted, sin cloud). Dejar `mem0-mcp-server`
como opción documentada si el self-hosted falla.

### Justificación
- `mem0-mcp` **no existe en PyPI** (404).
- `mem0-mcp-server` 0.2.1 funciona, pero su repo `mem0ai/mem0-mcp` está
  **archivado** y arrastra ~89 paquetes (openai, grpcio).
- `mcp-memory-service` 12.1.1 es self-hosted, sin cloud, verificado funcional.

### Alternativas
- `https://mcp.mem0.ai/mcp` (cloud de mem0, `type: "remote"`) — la sintaxis
  exacta del header de auth **NO VERIFICADA**. Requiere `MEM0_API_KEY` cloud.
- Escribir un servidor de memoria propio (Fase 2 demuestra que se puede) — más
  trabajo, pero el máximocontrol. **Es el plan B si los dos fallan.**

---

## 2026-10-18 — AD-0008: Qiskit directo como motor, MCP como orquestación

### Problema
¿Usar `mcp-qiskit` para el trabajo cuántico real, o Qiskit directo?

### Decisión
`mcp-qiskit` solo para **aprender el protocolo** (Fase 1) y **demostrar la
integración multi-MCP** (Fase 3). Para QAOA, valores esperados y ruido:
**Qiskit directo** en el `.venv` (`--extra quantum`).

### Justificación
Bugs verificados en `mcp-qiskit` que lo hacen inservible como motor:
- `statevector` se devuelve como **strings** (`"0.707+0j"`), no numérico →
  inútil para aritmética y gráficos.
- `run_circuit` **degrada en silencio** a un simulador genérico si el backend
  no existe (falsa simulación).
- Gates paramétricos sin `params` reciben **defaults silenciosos** (`rx`→0.5) →
  circuitos incorrectos sin error. Peligroso para un objetivo de aprendizaje.
- No hay simuladores ruidosos reales ni acceso a hardware IBM.
- Es **stateless**: hay que reenviar el dict del circuito en cada llamada.

El MCP queda como **capa de orquestación**; el motor es Qiskit directo.

### Alternativas
- Solo `mcp-qiskit` — descartado por los bugs de correctitud.
- Solo Qiskit directo, sin MCP cuántico — se pierde la demostración de
  orquestación multi-MCP (que es un objetivo del proyecto).

---

## 2026-10-18 — AD-0007: `TypedDict` para el estado del grafo, Pydantic para datos

### Problema
LangGraph permite estado como `TypedDict` o modelo Pydantic. ¿Cuál?

### Decisión
`State` del grafo = `TypedDict` con `Annotated[..., reducer]`.
Pydantic solo para los esquemas de datos (`Asset`, `Metrics`, `Portfolio`).

### Justificación
- Es lo que recomienda la documentación de LangGraph v1.
- Pydantic como estado tiene limitaciones: validación runtime **solo en la
  entrada del primer nodo**, la salida del nodo **no** es instancia del modelo
  (es dict), coerción silenciosa de tipos (`"42"`→`42`), y recursión de
  validación lenta.
- `TypedDict` encaja con el patrón de reducers, que necesitamos para el dict
  del circuito cuántico entre nodos.

### Alternativas
- Pydantic como estado — descartado por las limitaciones documentadas arriba.
- `MessagesState` con `AnyMessage` — necesario solo si hay mensajes de chat;
  el estado de cartera es estructurado.

---

## 2026-10-18 — AD-0006: `ClientSessionGroup` de MCP v2 (no `MultiServerMCPClient`)

### Problema
Hay que conectar 2-3 servidores MCP a un grafo LangGraph sin colisiones de
nombres.

### Decisión
Envolver `mcp.ClientSessionGroup` (SDK v2) en
`src/quantum_portfolio/mcp_clients/session_group.py`.

### Justificación
- `ClientSessionGroup` **fusiona** herramientas de N servidores en un solo
  namespace y da **protección de colisiones** gratis (`component_name_hook`,
  y error duro si un nombre se repite).
- `langchain-mcp-adapters` (el camino anterior) está **archivado**.
- `langchain.mcp.MCPAdapter` (el reemplazo oficial) está construido sobre
  `fastmcp` v4, no sobre `mcp` v2 → evita el conflicto en vez de resolverlo, y
  está en beta.

### Alternativas
- `langchain-mcp-adapters` — archivado, pinea `mcp<2`.
- `langchain.mcp.MCPAdapter` — beta, otra pila (`fastmcp` v4).
- Clientes `Client` separados por servidor — no fusiona namespaces, colisiones
  garantizadas sin trabajo extra.

---

## 2026-10-18 — AD-0005: Cliente MCP propio sobre MCP SDK v2

### Problema
`langchain-mcp-adapters` pinea `mcp<2.0.0` y está archivado. ¿Con qué SDK
conectar MCP a LangGraph?

### Decisión
`mcp>=2.3.0` (SDK oficial v2) y escribir un adaptador propio de ~30 líneas:
`Client.list_tools()` → `StructuredTool` con `args_schema` del `input_schema` →
`ToolNode`.

### Justificación
- Es la única vía con `mcp` v2 oficial + control fino del orquestador.
- `mcp` v1 está en pínea de mantenimiento (bugfixes y seguridad, sin features).
- Escribirlo obliga a entender el ciclo `list_tools()` → `call_tool()`, que es
  **el objetivo de aprendizaje de la Fase 1-2**.

### Alternativas
- `Quedarse en mcp<2` (lo que sugiere el propio SDK si tu paquete depende de
  él) — tentador, pero con la API congelada.
- `MCPAdapter` de LangChain — beta, otra pila.

---

## 2026-10-18 — AD-0004: Pin `mcp<2` para los servidores externos

### Problema
`financial-mcp-server` y `mcp-qiskit` declaran `mcp[cli]>=1.0.0` sin cota
superior. uv instala `mcp` v2, donde `FastMCP` → `MCPServer` y
`mcp.server.fastmcp` no existe. **Ambos fallan al arrancar.**

### Decisión
Todos los comandos de arranque incluyen el pin:
```bash
uvx --from financial-mcp-server --with "mcp<2" financial-mcp
uvx --from "mcp-qiskit[mcp]" mcp-qiskit   # el extra [mcp] trae fastmcp
```

### Justificación
Verificado ejecutando. Ninguna de las dos documentaciones upstream menciona el
pin. Sin él, **el proyecto no arranca**.

### Alternativas
- Fork y parchear los dos paquetes — demasiado trabajo para el objetivo.
- Esperar a que los mantenedores migren a v2 — ambos proyectos están casi
  abandonados.

---

## 2026-10-18 — AD-0003: MyST Markdown notebooks (`.md`) sobre JSON

### Problema
Los notebooks son JSON con una línea gigante por celda → diffs ilegibles en git
y GitHub no los renderiza bien.

### Decisión
`theory/*.md`: Markdown que se ejecuta con `myst-nb`, renderizado
nativamente en GitHub, diffs en texto legible línea a línea.

### Justificación
- Diffs legibles: clave para un repo público de aprendizaje donde el
  historial **es** la bitácora.
- Se ejecutan con `myst-nb`, las salidas se commitean, GitHub las renderiza.
- Los ejercicios usan `<details><summary>` (HTML dentro de Markdown), soportado
  por MyST.

### Alternativas
- `.ipynb` JSON — máxima compatibilidad Jupyter/Colab, pero diffs ilegibles.
- `.md` sin ejecución — se pierde ejecutar y verificar los ejemplos; este es un
  proyecto donde **verificar** es el objetivo.

---

## 2026-10-18 — AD-0002: `theory/` transversal, no por fase

### Problema
¿Notebooks por fase, o un curso continuo?

### Decisión
`theory/` con 12 notebooks **temáticos** (no por fase). Cada README de fase
enlaza a los que hay que leer antes de empezar esa fase.

### Justificación
- Un tema (QAOA, MCP) atraviesa varias fases. Organizarlo por fase lo
  fragmentaría.
- El conocimiento es permanente, no desechable como los `labs/`.
- Permite que la Fase 4 use lo aprendido en la Fase 1.

### Alternativas
- Notebooks dentro de cada `labs/phaseN/` — se pierden al cerrar la fase.
- `docs/*.md` sin ejecución — no se puede verificar.

---

## 2026-10-18 — AD-0001: `labs/` separado de `src/`

### Problema
El código de aprendizaje (feo, desechable, sin tests) y el paquete real
(importable, testeado) mezclados en un solo sitio.

### Decisión
`labs/` = cuaderno desechable. `src/quantum_portfolio/` = paquete real. El
código se **promueve** de `labs/` a `src/` al cerrar cada fase.

### Justificación
El error clásico es acabar con un paquete lleno de scripts de tutorial y un
80% de cobertura que no importa. Separar permite aprender sin ensuciar lo que
se importa.

### Alternativas
- Un solo `src/` con subcarpetas por fase — un solo lugar, pero mezcla.
- Solo `labs/` — reescribir todo al final cuando quieras empaquetar.
- Detalle completo en [`../docs/adr/0002-separate-labs-from-src.md`](../docs/adr/0002-separate-labs-from-src.md).

---

## Decisiones heredadas (del brainstorming inicial)

| # | Decisión | Alternativa descartada |
|---|---|---|
| — | uv como gestor único | venv+pip (menos reproducible) |
| — | Python 3.12 | 3.13 del sistema (conflictos con Qiskit/LangChain) |
| — | LangGraph antes que CrewAI | CrewAI primero (dificulta aprender grafos de estado) |
| — | Git desde el día 1, 1 commit por tarea | Commits solo por fase (se pierde el detalle) |
| — | Sin `gh` CLI (el remoto ya existía) | Instalar gh (innecesario sin PRs) |