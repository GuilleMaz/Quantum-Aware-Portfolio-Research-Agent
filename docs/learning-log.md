# Bitácora de aprendizaje

> **Qué es esto.** Registro semana a semana de **qué aprendí**, no de **qué
> hice**. `project-memory/changelog.md` dice qué cambió en el repo. Este fichero
> dice qué cambió en quien lo escribió.

Una entrada de changelog que dice `fix(mcp): cliente stdio con ClientSessionGroup`
no enseña nada por sí sola. La bitácora existe para capturar el momento en que
algo **dejó de ser obvio**. Si dentro de seis meses vuelvo a perder dos horas
con el mismo problema, esta bitácora es lo que me lo ahorra.

**Regla de oro:** una entrada que no contiene al menos un "no sabía que" no
entra. Si solo documenté pasos que ya conocía, no era aprendizaje, era
ejecución.

---

## Cómo usar esta bitácora

Cada entrada sigue la convención:

```
### AAAA-MM-DD — Fase N — Tema corto

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**
- **Pendiente:**
```

- **Qué funcionó** — el mecanismo que entendí. Debe poder explicarse en dos
  frases sin jerga.
- **Qué me sorprendió** — lo contrario de lo que esperaba. Esta es la sección
  más valiosa y la que más se tiende a omitir.
- **Trampas / pitfalls** — el fallo concreto, con el síntoma exacto. Sin esto no
  sirve para nada.
- **Qué apliqué** — el cambio en el código o en el diseño. Si no apliqué nada,
  está bien decirlo: aún no era el momento.
- **Pendiente** — lo que queda abierto para la siguiente sesión.

Las entradas se añaden **al principio** de la sección de su fase, en orden
cronológico inverso. No se editan entradas antiguas: si me equiviqué, añado una
entrada que diga que me equivoqué.

**Las subsecciones marcadas con `> Pendiente: rellenar tras la fase` son
plantillas.** Tienen los prompts que hay que responder, no respuestas. No las
rellenes con suposiciones: si no lo has ejecutado, no lo escribas.

---

## Fase 1 — Fundamentos de MCP

### El ciclo `list_tools()` → `call_tool()`

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts para responder:

- ¿Qué pasa exactamente entre que el cliente escribe `tools/list` en stdin y
  recibe la lista? ¿En qué punto se lanza el proceso del servidor?
- ¿Cuándo ocurre el handshake `initialize` respecto a `tools/list`? ¿Se puede
  llamar a una herramienta sin haber inicializado?
- ¿Qué información devuelve `initialize` (capacidades, versión de protocolo,
  info del servidor) y qué se puede hacer con ella?
- ¿`list_tools()` se llama una vez al conectar o el cliente lo re-lista? ¿Qué
  pasa si una herramienta aparece mientras la sesión está abierta?
- ¿Cuál fue el primer error que vi, y qué mensaje dio? (Anotar el literal, no la
  descripción.)

### Transportes: stdio y los demás

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- En stdio, ¿quién cierra qué y en qué orden? ¿Qué pasa si el hijo muere?
- ¿Qué otros transportes existen (HTTP+SSE, streamable HTTP) y por qué el
  proyecto usa stdio?
- ¿Cuántos procesos hay en la mesa? Dibujarlo. ¿Quién es el padre, quién el
  hijo, quién escucha a quién?
- ¿Qué pasa con el proceso hijo cuando el cliente se desconecta? ¿Queda
  zombi?

### Por qué las descripciones son contratos

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- Comparar la descripción de una herramienta buena con una mala de las 42 del
  servidor financiero. ¿Qué información contiene cada una?
- ¿Qué pasa si el nombre de la herramienta es bueno pero la descripción es
  ambigua? ¿Y al revés?
- ¿Qué parte del prompt decide realmente la elección: nombre, descripción,
  esquema de entrada, o el contexto de la conversación?
- ¿Cambia el resultado si la descripción está en español o en inglés? Probarlo.
- ¿Qué es peor: una descripción demasiado corta o demasiado larga?

### El doble encoding JSON

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Qué llega exactamente en `structured_content` y qué llega en `content`?
  Poner los dos literales, sin abreviar.
- ¿Cuántas capas de JSON hay? Contarlas sobre un ejemplo real.
- ¿Qué pasa si solo miro `content`? ¿Y si solo miro `structured_content`?
- ¿Cuándo envuelve escalares en `{"result": N}` y cuándo no?
- Escribir el `json.loads` encadenado que hace falta. ¿Cuántos hace falta?

### `mcp-qiskit` es stateless

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Qué pasa **exactamente** si no reenvío el dict del circuito en el segundo
  `add_gate`? Describir el síntoma literal, no "da error".
- ¿El servidor se quejó? ¿O aceptó la llamada y produjo un circuito vacío?
- ¿Cuánta información viaja de vuelta en cada llamada? ¿Es un dict plano o un
  objeto serializado?
- ¿Cómo se sabe a partir del dict que el circuito está bien formado?
- ¿Qué frase del README de `mcp-qiskit` es **falsa**? Copiarla literal.

### Fallos silenciosos de los gates paramétricos

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Qué pasa con `rx` sin `params`? ¿Qué ángulo se usa por defecto y por qué es
  0.5 y no 0?
- ¿Qué pasa con `u3` sin `params`? ¿Qué circuito sale?
- ¿Cómo se detecta el error *después*, cuando ya se ha enviado al orquestador?
  ¿Hay alguna defensa?
- ¿Qué otros servidores de herramientas podrían tener el mismo fallo? Pensar en
  el patrón: valor por defecto silencioso en un parámetro obligatorio.

---

## Fase 2 — Mi primer MCP server

### Escribir un servidor desde cero

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Cuántas líneas hay entre la función y que aparezca en `tools/list`? ¿Qué
  hace el decorador exactamente?
- ¿Cuándo arranca el proceso? ¿Qué se ejecuta al importar el módulo y qué se
  ejecuta en cada llamada?
- ¿Qué pasa si la función lanza una excepción? ¿Llega al cliente como error o
  revienta el servidor?
- ¿Qué firma tiene `main` y por qué el servidor se queda vivo sin hacer nada?

### De tipos de Python a JSON Schema

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- Poner el JSON Schema generado por `a: int, b: int`. ¿Qué más aparece que no
  escribí yo?
- ¿Qué pasa con `list[float]`, `dict[str, float]`, `Literal`, `datetime`?
- ¿Qué tipos **no** tienen traducción directa? ¿Qué pasa entonces?
- ¿Qué pasa con los valores por defecto? ¿Van al schema como `required` o no?
- ¿Se puede forzar una descripción por parámetro? ¿Cómo se hace?

### El docstring como contrato

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Qué parte del docstring llega al cliente? ¿La primera línea, todo, el
  formato `Args:`?
- Reescribir el docstring de `loan_emi` para que el LLM la elija antes y después
  de la prueba. ¿Cuánto cambia el resultado?
- ¿Qué información **no** cabe en un docstring pero el LLM necesitaría?
  ¿Dónde ponerla?

### MCP Inspector

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Qué se ve en el Inspector que no se ve en el cliente? ¿Y al revés?
- ¿Qué se puede probar sin escribir un solo cliente?
- ¿Cómo se ve el JSON-RPC crudo? Anotar el mensaje exacto de `tools/call`.
- ¿Cuánto cuesta levantar el Inspector en esta máquina? (minutos)

### Diseño de la descripción para que el LLM elija bien

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Cuántas iteraciones hicieron falta hasta que el LLM eligió `loan_emi` sin
  nombrarla? Contarlas. Este número es el indicador de éxito de la fase.
- ¿Qué palabras de la pregunta del usuario aparecen en la descripción de la
  herramienta que ganó? ¿Coinciden literalmente?
- ¿Crear una herramienta gemela con descripción casi idéntica cambia algo?
  ¿Cuál gana?
- ¿Qué pasa si dos herramientas se solapan en propósito? ¿Cómo se desambigua?
- ¿Qué hace el LLM cuando **ninguna** encaja? Inventa? ¿Te lo dice?

---

## Fase 3 — Orquestación con LangGraph

### TypedDict vs Pydantic

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Qué ventaja tiene `TypedDict` aquí frente a Pydantic, siendo Pydantic la
  opción obvia?
- ¿Qué error se paga por no validar el estado? ¿Se dio el caso?
- ¿Dónde aparece el `Annotated[...]` y por qué ese sitio y no otro?
- ¿Qué pasa si un nodo devuelve una clave que no está en el estado?

### Reducers: por qué existen

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- Reproducir el fallo: dos nodos devuelven un dict y el segundo pisa al
  primero. Poner el traceback literal.
- ¿Qué hace el reducer por defecto (`operator.add`)? ¿Por qué?
- Escribir `merge_circuit` a mano. ¿Qué regla debe cumplir?
- ¿Qué otras claves del estado necesitan reducer y cuáles no? Justificar cada
  una.
- ¿Qué pasa si el reducer muta el valor que recibe en vez de devolver uno
  nuevo?

### Conditional routing

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Dónde se lee el estado para decidir? ¿Qué firma tiene la función de
  condición?
- ¿Qué pasa si la función devuelve un valor que no está en el `path_map`?
- ¿Se puede ramificar a **dos** nodos a la vez? ¿Tiene sentido aquí?
- ¿Quién decide, el grafo o el LLM? ¿Son la misma cosa?
- ¿Cuándo merece la pena que un LLM decida el routing y cuándo una condición
  determinista?

### Checkpointer y `thread_id`

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Qué se guarda exactamente en el checkpoint? ¿Todo el estado, o solo
  referencias?
- ¿Qué pasa si el mismo grafo se invoca con el mismo `thread_id` desde dos
  sitios a la vez?
- ¿Y con `thread_id` distinto? ¿Se pisan?
- ¿Qué se ve en `aget_state_history()`? Volcar la salida real.
- ¿Cuándo hay que cerrar el saver? ¿Qué pasa si no se cierra?

### Depurar un flujo multi-paso

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Cuál fue el bug más difícil de encontrar? ¿Cuánto tiempo? ¿Cómo se
  debuggea un grafo en `stream()`? Poner el fragmento de código que lo hizo
  posible.
- ¿Qué información falta cuando el grafo "simplemente no llega"? ¿Qué
  instrumentaste?
- ¿Qué herramientas hay para inspeccionar el estado en un punto dado?
- ¿Qué es más difícil de depurar en LangGraph que en un script lineal, y qué se
  hace al respecto?

---

## Fase 4 — Memoria y comparación

### Memoria corta vs memoria larga

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Qué estado vive en el checkpointer y qué vive en el servidor de memoria?
  ¿Quién manda sobre quién?
- ¿Qué es "no olvidar" y qué es "no recuperar"? ¿Qué se recupera por defecto?
- ¿Cuándo se escriben las conclusiones al almacén de memoria y quién decide qué
  se guarda?
- ¿Qué pasa si el almacén crece sin límite? ¿Hay poda?

### Embeddings y búsqueda semántica

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Qué modelo de embeddings usa el servidor? ¿Local o remoto? ¿Cuánto cuesta?
- ¿La búsqueda es semántica o por keywords? Probarlo con dos consultas que
  usan palabras distintas para lo mismo.
- ¿Qué se indexa: la conclusión, el razonamiento, o la cartera entera?
- ¿Qué se pierde al comprimir un análisis a un embedding?

### LangGraph vs CrewAI

> Pendiente: rellenar tras la fase

- **Qué funcionó:**
- **Qué me sorprendió:**
- **Trampas / pitfalls:**
- **Qué apliqué:**

Prompts:

- ¿Cuánto código hay que reescribir para portar el mismo grafo? ¿Cuántas líneas
  cambian y cuántas se pueden copiar tal cual?
- ¿Qué concepto de CrewAI no tiene equivalente en LangGraph, y al revés?
- ¿Qué framework cuesta más tokens? ¿Medido o estimado?
- ¿Cuál de los dos se ajusta mejor a **este** problema (routing
  determinista + estado grande + herramientas MCP)?
- ¿Qué harías distinto si tuvieras que empezar de cero hoy?

---

## Fuentes

**Regla:** solo se citan referencias **verificadas**. Si la referencia no se
puede comprobar, se marca explícitamente como `**NO VERIFICADO**` y se explica
por qué. Nunca se rellena una cita de memoria: una referencia inventada en un
proyecto cuyo objetivo es el rigor contamina todo lo demás.

Formato: Autor(es), *Título*, **revista o preprint**, volumen/página o número
arxiv, año. Con DOI o arXiv cuando exista.

### Verificadas (a 2026-10-18)

- Farhi, Goldstone & Gutmann, *A Quantum Approximate Optimization Algorithm*,
  arXiv:1411.4028 (2014). — El paper fundacional de QAOA.
- Buonaiuto et al., *Best practices for portfolio optimization by quantum
  computing*, Sci. Rep. **13**, 4096 (2023).
  DOI: 10.1038/s41598-023-36174-z
- Brandhofer et al., *Benchmarking the performance of portfolio optimization with
  QAOA*, Quantum Inf. Process. **22**, 25 (2022). DOI: 10.1007/s11128-022-00950-6
- Certo, Pham & Beaulieu, arXiv:2203.04912 (2022).
- Stopfer & Wagner, *Quantum Portfolio Optimization: An Extensive Benchmark*,
  arXiv:2509.17876 (2025).
- Rebentrost & Lloyd, *Quantum Computational Finance*, KI **38**, 327 (2024).
  DOI: 10.1007/s13218-023-00480-5

### NO VERIFICADO

> Pendiente: rellenar durante las fases. Añadir aquí toda referencia que se
> quiera citar y no se haya podido comprobar, con el motivo.

- **NO VERIFICADO** — El tutorial `mcp-intro` citado en la planificación
  original. **No existe como repositorio público.** Comprobado el 2026-10-18.
  Sustituido por los ejemplos oficiales del SDK y la spec.
- **NO VERIFICADO** — Sintaxis del header de autenticación de
  `mcp-memory-service` contra el servidor cloud `https://mcp.mem0.ai/mcp`. Sin
  comprobar; la decisión de la Fase 4 es usar el self-hosted y evitarlo.
- **NO VERIFICADO** — Cualquier afirmación sobre capacidad computacional de
  hardware cuántico actual que no venga con referencia a un paper. Si no hay
  cita, no va aquí: no va a ningún sitio.

### Nota sobre el estado del arte

Las citas de arriba son de 2022–2025 y el campo se mueve. El backlog de
`TASKS.md` incluye una tarea de revisión anual. Si una referencia queda
obsoleta, se marca aquí, no se borra en silencio.