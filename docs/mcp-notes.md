# Notas del protocolo MCP

> **Estas son notas de trabajo**, no documentación oficial. Se actualizan
> durante las fases 1 y 2, mientras se toca el protocolo crudo. Cuando se cierre
> la fase 2, se decide si este cuaderno se congela o se mantiene.
>
> Si algo aquí contradice a la spec de MCP, **la spec gana** y se corrige esta
> nota. Si contradice al comportamiento observado, se documenta el
> comportamiento con su versión y su comando de arranque.

`docs/learning-log.md` registra el aprendizaje. Este fichero registra los
**hechos técnicos verificables**. Separados a propósito: uno es
interpretación, el otro es referencia.

---

## El ciclo

Tres mensajes JSON-RPC, en este orden. No es negociado, es fijo:

```
cliente ──initialize──► servidor      ¿quién eres, qué sabes hacer?
cliente ◄────result──── servidor      protocolo, capacidades, info

cliente ──tools/list──► servidor      ¿qué tienes?
cliente ◄────result──── servidor      lista de herramientas + esquemas

cliente ──tools/call──► servidor      usa esta con estos argumentos
cliente ◄────result──── servidor      contenido, structured_content, is_error
```

**Qué envuelve JSON-RPC 2.0:** exactamente esto. MCP no es un formato de datos
nuevo; es una capa de descubrimiento e invocación sobre JSON-RPC 2.0. El
`jsonrpc: "2.0"` y el `id` correlativo son JSON-RPC puro, no MCP.

JSON-RPC 2.0 define:

| Campo | Rol |
|---|---|
| `jsonrpc` | Versión del protocolo de transporte: `"2.0"` |
| `id` | Correlación petición-respuesta. Ausente en notificaciones |
| `method` | `"initialize"`, `"tools/list"`, `"tools/call"` |
| `params` | Argumentos |
| `result` | En éxito |
| `error` | En fallo, con `code`, `message`, opcionalmente `data` |

MCP **añade** sobre eso: el bloque `capabilities`, el campo `protocolVersion`,
y los métodos `tools/list` y `tools/call` con sus esquemas. Nada más. Por eso
`initialize` se parece a cualquier otro handshake: es un `hello` que además
dice qué hay detrás.

**Pendiente de documentar:** el contenido literal de la respuesta a
`initialize` de cada uno de los tres servidores, y en qué difieren sus bloques
`capabilities`.

---

## Transporte stdio

El caso por defecto del proyecto. El cliente **lanza el servidor como
subproceso** y habla con él por sus dos descriptores estándar.

```
┌────────────┐   stdin (escribe JSON-RPC)   ┌──────────────┐
│  cliente   │ ───────────────────────────► │  servidor    │
│            │                              │  (subproceso)│
│            │ ◄─────────────────────────── │              │
└────────────┘   stdout (lee JSON-RPC)       └──────────────┘
                                           ┌──────────────┐
                                           │  stderr      │  ← logs, banners
                                           └──────────────┘
```

### Los dos descriptores son un contrato strict

- **stdin**: el cliente escribe. El servidor lee.
- **stdout**: el servidor escribe. El cliente lee.
- **stderr**: el servidor escribe. **Nadie lo lee como protocolo.**

**Por qué los `print()` a stdout ROMPEN el protocolo.** stdout no es un canal
libre: es por donde viaja el JSON-RPC. Si el servidor hace
`print("iniciando...")`, ese texto se intercala en el flujo como si fuera una
respuesta. El cliente, que espera una línea JSON, recibe:

```
iniciando...
{"jsonrpc":"2.0","id":1,"result":{...}}
```

El resultado depende de la robustez del parser del cliente, y esa es la parte
peor: **puede no fallar**. Puede ignorar silenciosamente la línea basura, o
fallar con un error de parseo que no señala la causa real. En el peor caso
descorrelaciona respuestas y los errores que aparecen son de RPC, no de
sintaxis. Este es el tipo de bug que cuesta una tarde.

La regla: **stdout es solo JSON-RPC. Todo lo demás va a stderr.**

```python
import sys
print("iniciando servidor")          # MAL: rompe el protocolo
print("iniciando servidor", file=sys.stderr)   # BIEN
```

En Python, `logging` ya escribe a stderr por defecto, así que la mayoría de las
veces esto sale gratis. El problema aparece con `print()`, con banners
impresos a mano, y con cualquier librería que imprima a stdout.

### El caso del banner de FastMCP

Los servidores basados en FastMCP (`MCPServer` en SDK v2) imprimen un banner
ASCII de arranque. Va **a stderr**, precisamente porque el servidor respeta el
contrato. Por eso el MCP Inspector puede mostrarlo en su consola sin romper nada,
y por eso OpenCode muestra esa caja con las herramientas disponibles sin que sea
un error.

Es un buen ejemplo de la regla: el servidor quiere ser vistoso y puede, porque
eligió el canal correcto.

**Consecuencia práctica para este repo:** si alguna vez un `print()` nuestro
rompe la conexión, el diagnóstico es mirar el primer stdout, no el último error.

---

## La diferencia entre un servidor MCP y "un paquete de tools"

Es la distinción central del proyecto, y la que justifica que la Fase 1 exista.

Un "paquete de tools" es una función que llamas importando:

```python
from mis_tools import get_price        # tú decides el transporte,
get_price("AAPL")                      # tú decides el proceso,
                                       # tú escribes el parseo del resultado
```

Un **servidor MCP** es otra cosa. Tres diferencias, en orden de importancia:

1. **Vive en otro proceso.** Lo arranca el cliente, no tú. Se comunica por un
   canal estandarizado. Las dependencias del servidor son suyas, no tuyas: 97
   paquetes de Qiskit para `mcp-qiskit` no tocan tu `.venv`.
2. **Anuncia sus capacidades al arrancar.** `initialize` devuelve protocolo,
   capacidades (soporte, recursos, prompts, herramientas, logging) e info. No
   es un detalle: es lo que permite a un cliente saber con qué puede hablar en
   lugar de llamar a ciegas.
3. **Negocia versión de protocolo.** `protocolVersion` en el handshake, con
   reglas de degradación si no coincide. La versión se negocia, no se asume.

### Por qué esto permite que el mismo servidor valga para todos

Porque **el cliente** decide cómo hablar, no el servidor. El único punto de
contacto son los mensajes JSON-RPC sobre stdio, y ese contrato está
especificado.

El mismo `financial-mcp-server` funciona en OpenCode, en Claude Desktop y en
Cursor **sin cambiar una línea**, porque los tres implementan el mismo lado del
protocolo. El servidor no sabe cuál es. Y por eso se puede añadir un cuarto
cliente, o cambiar de cliente, sin tocar el servidor.

La alternativa (un paquete importable) no tiene esa propiedad: el destino de
los datos está cableado en el import.

> **Matiz honesto:** que el servidor sea portable no significa que su
> *comportamiento* lo sea. Las variables de entorno, el `PATH`, la codificación
> de la consola y el directorio de trabajo **sí** cambian entre clientes. La
> portabilidad es del protocolo, no del entorno. Ver `config/clients/*.example.json`,
> donde la ruta absoluta a `uvx.exe` es obligatoria por esto.

---

## Tool discovery: cómo decide el LLM

Cuando un servidor anuncia herramientas, cada una viaja con tres cosas:

| Campo | Qué es | Peso real para el LLM |
|---|---|---|
| `name` | Identificador único | Alto. Es lo que se emite al llamar |
| `description` | Texto libre que el autor escribe | **El más alto.** Es lo único que dice cuándo usarla |
| `inputSchema` | JSON Schema de los parámetros | Medio. Restringe lo que se puede llamar, no decide si se llama |
| `title` | Nombre legible para UI | Nulo para el modelo, alto para una persona |

El razonamiento del LLM es aproximadamente: *¿esta herramienta resuelve lo que
me han pedido?* La única fuente de ese "¿cuándo usarla" es la `description`. El
`name` elegante pero ambiguo con veinte herramientas parecidas
(`get_price`, `get_prices`, `get_price_history`, `get_quote`, `search_price`).

### Por qué el prompt importa más que el nombre

El nombre es un identificador técnico. La descripción es un **contrato de
comportamiento**. Lo que distingue a un buen diseño de uno malo no es cómo se
llama la función, sino qué le promete al LLM y en qué condiciones.

Comparación mental, que es exactamente lo que hay que hacer en la tarea 2.9:

```
get_price(ticker)             → calcula el precio. Úsala cuando: ?
compound_interest(...)        → ✔ "Devuelve el capital final tras n periodos a
                                una tasa fija anual. Úsala para cálculos de
                                capital compuesto, no para amortización de
                                préstamos (usa loan_emi). Entradas: principal
                                en la moneda, rate como fracción decimal
                                (0.08 = 8%), periods como años enteros."
```

La segunda descripción dice **qué hace**, **cuándo usarla**, **cuándo no**,
**y cómo se codifican las unidades**. Eso es un contrato. La primera es el
nombre de una función con un punto y paréntesis.

Tres efectos practical:

1. **Las unidades implícitas son un bug esperando.** Si el LLM cree que `rate`
   es 8 y le pasa 8, el resultado es 8ⁿ veces mayor y no hay error. Declarar
   `rate: float` en el schema no dice si es 0.08 o 8.
2. **La negación es información.** Decir "no uses X para Y" desambigua
   herramientas solapadas mejor que añadir otra herramienta.
3. **Los ejemplos en la descripción valen más que los ejemplos aparte.** El
   LLM lee la descripción en el prompt de sistema, junto a la herramienta. Un
   ejemplo en el `description` está en el sitio correcto; un ejemplo en el README
   del repo no está en el prompt.

**Por qué esto es diseño de interfaz y no documentación:** el criterio de éxito
de la Fase 2 es que el LLM elija bien **sin que le digas el nombre** (tarea
2.8). Si hay que nombrarla, el contrato está mal escrito. Eso no se arregla
añadiendo una nota al README.

---

## Resultados: los tres campos

Toda respuesta a `tools/call` trae tres cosas. Mirar solo una es el error más
frecuente.

```python
class CallToolResult:
    content: list[ContentBlock]        # lo que ve un humano
    structured_content: dict | None    # lo que debería ver una máquina
    is_error: bool                     # el éxito está aquí, no en una excepción
```

### `content`

Bloques de contenido: texto, imagen, audio, o `resource`. Es la parte pensada
para renderizarse. **Es legible pero no parseable.** Nunca hagas aritmética
sobre `content`.

### `structured_content`

Datos estructurados. Cuando el servidor lo declara (`outputSchema` /
`structuredContent`), cumple un schema y es parseable. Es lo que debes usar.

### `is_error`, no una excepción

**Los errores de herramienta no lanzan excepción.** Vuelven como una respuesta
normal con `is_error=True`. El SDK no considera que un fallo de la herramienta sea
un fallo de la llamada: la llamada funcionó, la herramienta no.

```python
result = await session.call_tool("no_existe", {})
if result.is_error:          # hay que comprobarlo explícitamente
    ...
```

Si no lo compruebas, un error se lee como un resultado. Con una herramienta que
devuelve texto, la diferencia entre "no encontró nada" y "falló al buscar" es
inexistente si no miras el flag. Es la fuente más común de agentes que
"funcionan" y están equivocados.

### El doble encoding JSON

Dos capas, dos sitios distintos del protocolo:

**Capa 1 — el resultado del servidor.** Cuando un servidor serializa su propia
respuesta a JSON *dentro* del campo de contenido, el cliente recibe una **string
que contiene JSON**:

```json
{ "result": "{\"price\": 189.5, \"currency\": \"USD\"}" }
```

Se necesita un `json.loads` para el exterior y otro para la string interior:

```python
outer = json.loads(result.structured_content["result"])
data  = json.loads(outer)      # ← el segundo, el que se olvida
```

Omitir el segundo `json.loads` es la causa más común de un `TypeError: string
indices must be integers` en este proyecto. Tarea 1.7: reprodúcelo a
deliberadas y anótalo.

**Capa 2 — los escalares envueltos.** Cuando el servidor devuelve un escalar, no
lo devuelve crudo dentro de `structured_content`; lo envuelve:

```python
structured_content == {"result": 42}     # no 42
```

Tarea 3.5: comprobarlo. Afecta a cualquier herramienta que devuelva un número
suelto, y es el motivo de que `["result"]` aparezca en tanto código.

**Las dos capas aparecen juntas.** Peor caso, y el que se verá en el servidor
financiero: `{"result": "42"}` (string dentro de dict), o
`{"result": "{\"price\": 189.5}"}`. Comprobado en la 1.7, anotado en la bitácora.

---

## Entorno del hijo

**El cliente MCP no hereda el entorno del padre.** Recibe una lista blanca.

El subproceso ve un subconjunto controlado de variables: en Windows,
`APPDATA`, `PATH`, `TEMP`, `TMP`, `USERNAME`, `USERPROFILE`, `LOCALAPPDATA`,
`SYSTEMROOT`, `WINDIR`... y poco más.

### Consecuencia: las API keys no llegan

Una variable que no está en la lista blanca **no existe** para el servidor. Si
el servidor lee `os.environ["FMP_API_KEY"]`, no ve lo que el usuario acaba de
escribir en su `.env`: ve un `KeyError`. Y como el fallo ocurre en el subproceso,
no en el cliente, el error llega como `is_error=True` con un mensaje que no
menciona el entorno en absoluto.

**Solución:** pasar el entorno explícitamente.

```python
stdio_params = StdioServerParameters(
    command="...",
    args=[...],
    env={**os.environ, "MI_CLAVE": valor},   # el hijo ve esto
)
```

`env=` **reemplaza**, no añade. Si solo pasas la clave que te interesa, el hijo
pierde `PATH` y deja de encontrar `uvx`. El patrón correcto es
`{**os.environ, "MI_CLAVE": valor}` — ampliar, no sustituir.

### Consecuencia Windows: `PATH` mínimo en clientes GUI

Un cliente lanzado desde el menú Inicio hereda un `PATH` tan corto que
`uvx.exe` no está. El síntoma es `NOT FOUND`, no un error de Python, y no
aparece desde la terminal (que sí tiene `PATH`). La diferencia entre un cliente
y otro es el entorno, no la configuración.

**Solución:** ruta **absoluta** a `uvx.exe` en `config/clients/*.example.json`.

---

## Errores y timeouts

### `read_timeout_seconds` es un `float`, no un `timedelta`

En el SDK de Python, los tiempos de espera son **segundos en coma flotante**:

```python
StdioServerParameters(..., read_timeout_seconds=60.0)     # correcto
StdioServerParameters(..., read_timeout_seconds=timedelta(seconds=60))  # MAL
```

Es una asimetría real con otros clientes y librerías del ecosistema, donde el
`timedelta` es lo habitual. El error no siempre es claro.

El valor por defecto no sirve para `mcp-qiskit`: **67 s** en el primer arranque
(97 paquetes), ~9 s en caliente. Por eso `timeout: 60000` en `opencode.json`, no
el default de 5000 ms.

### `-32001`

El rango reservado de JSON-RPC para errores de implementación
(`-32000` a `-32099`). MCP usa `-32001` para el **timeout de una petición**: el
cliente dejó de esperar y abandonó. No es un error del servidor: es un error del
cliente que se cansó.

Distinción práctica:

- **`-32602` (Invalid params)** → el servidor entendió la llamada y la rechazó
  por los argumentos. Es un problema del *llamante*.
- **`-32001`** → el servidor no respondió a tiempo. Puede ser arranque lento, o
  un deadlock. No dice nada sobre la validez de los argumentos.
- **`is_error=True`** → el servidor procesó la llamada y la herramienta falló.
  Puede ser un error de negocio, no de protocolo.

Confundir estos tres lleva a "arreglar" el código del cliente cuando el problema
era el arranque, o a subir timeouts cuando el problema eran los argumentos.

---

## La trampa de los dos servidores externos

**Ninguna documentación upstream lo menciona.** Se descubríó ejecutando.

Ambos paquetes declaran su dependencia como:

```
mcp[cli]>=1.0.0
```

Sin cota superior. uv resuelve a la **última versión mayor**, instala MCP 2.x, y
en 2.x `FastMCP` pasó a llamarse `MCPServer`: `mcp.server.fastmcp` ya no existe.
Los dos servidores importan de ahí y mueren al arrancar:

```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'
```

El mensaje no menciona la versión de MCP, no menciona la dependencia transitiva,
y no menciona `FastMCP` → `MCPServer`. Dice "no encuentro este módulo" y listo.
Se pierden tiempo revisando el código del servidor, que está perfectamente bien
escrito.

### El arreglo

Forzar la versión en el comando de arranque:

```powershell
uvx --from financial-mcp-server --with "mcp<2" financial-mcp
```

Tres cosas que hay que entender de esto:

1. **`--with` es una restricción del entorno efímero**, no una dependencia del
   paquete. El `pyproject.toml` del servidor sigue diciendo `>=1.0.0`.
2. **`mcp<2` no significa "MCP 1.x"**. Significa "cualquier versión anterior a
   la 2", lo cual incluye 1.0.
3. **No es un bug de uv.** uv hizo exactamente lo que le pidieron. El problema
   está en el `pyproject.toml` del servidor: un `>=` sin cota superior en una
   API con renombrados incompatibles es una promesa que no se puede cumplir.

> **Estado a 2026-10-18: workaround, no arreglo.** El fix upstream es que esos
> proyectos actualicen su dependencia o sus imports. Mientras no lo hagan, el
> `--with "mcp<2"` es la única vía. Está en los comandos verificados de
> `AGENTS.md` §2 y en el `README.md`.

> **NO VERIFICADO** — Si existe ya un PR o release upstream que arregle esto.
> No comprobado. No se afirma aquí que lo haya ni que no.

---

## Tabla de bugs verificados

Todos empíricos, 2026-10-18. Todos reproducidos antes de anotarse. La columna
"síntoma" es lo que se ve; "causa" es lo que lo produce.

### `mcp-qiskit`

| # | Síntoma | Causa |
|---|---|---|
| 1 | El `add_gate` con `rx` sin `params` no da error, y el circuito sale mal | Default silencioso: `rx` → 0.5 rad, `u3` → (0,0,0). **El fallo más peligroso del proyecto** |
| 2 | El `statevector` llega como `["0.7071067811865475+0j", ...]` | Números serializados con `str()`, no JSON numérico. Inutilizable para aritmética sin parsear |
| 3 | Pides density matrix y obtienes un simulador ideal | `run_circuit` degrada en silencio a `AerSimulator()` genérico si el backend no existe. **No confíes en el backend reportado** |
| 4 | El segundo `add_gate` sin reenviar el circuito no hace lo que esperas | El servidor es **stateless**, contra lo que dice su README. El circuito es un dict que se deserializa → ejecuta → reserializa en cada llamada |
| 5 | `seed=0` produce resultados no reproducibles | `seed if seed else 42`: el 0 es falsy y se convierte en 42. Semántica de Python filtrada en un boundary de API |
| 6 | `draw_circuit_tool("ascii")` revienta en consola Windows | Los caracteres de arte ASCII no son representables en cp1252. `PYTHONIOENCODING=utf-8` lo arregla |

### `financial-mcp-server`

| # | Síntoma | Causa |
|---|---|---|
| 7 | El histórico de precios llega siempre a 250 barras, pidas lo que pidas | Truncado a 250 bars en el servidor, sin opción para cambiarlo |
| 8 | No hay forma de obtener la lista de activos disponibles | Ninguna herramienta devuelve un "universo". **El universo vive en nuestro `config/`** |
| 9 | Rate limits de Yahoo Finance de forma intermitente | Mitigado por el autor con `curl_cffi` (impersona Chrome) + caché de 120 s en proceso |
| 10 | El resultado viene como `{"result": "<json string>"}` | Doble encoding. Dos `json.loads` o no hay datos utilizables |

### Transversal (SDK y entorno)

| # | Síntoma | Causa |
|---|---|---|
| 11 | El error no lanza excepción, se lee como resultado | `is_error=True` en `CallToolResult`. Comprobar siempre |
| 12 | `structured_content` devuelve `{"result": 42}` y no `42` | Los escalares se envuelven |
| 13 | El hijo no ve `MI_API_KEY` | Lista blanca de entorno, no herencia. `env={**os.environ, ...}` |
| 14 | `uvx` da `NOT FOUND` desde un cliente GUI | `PATH` mínimo. Ruta absoluta a `uvx.exe` |
| 15 | Timeout del primer arranque de `mcp-qiskit` | 67 s (97 paquetes). `read_timeout_seconds=60.0`, no `timedelta` |
| 16 | La respuesta se corta o se corrompe sin error claro | Un `print()` a stdout en el servidor, mezclado con el JSON-RPC |

### Nota sobre el uso de esta tabla

Estos bugs son de **software de terceros en versiones concretas**. Cuando se
actualice cualquiera de los dos servidores, esta tabla puede quedar obsoleta.
Verificarla, no heredarla. Si un bug sigue ahí, se queda con su fecha. Si ya no,
se borra con una nota de cuándo desapareció — no en silencio.

---

## Pendiente de documentar

Secciones a completar durante las fases. Cada una con la razón por la que
todavía no está.

### Fase 1

- [ ] **Capacidades reales por servidor** — el bloque `capabilities` que devuelve
      `initialize` en cada uno de los tres. Comparar: ¿anuncian más de lo que
      cumplen?
- [ ] **Literales de `initialize`** — copiar la respuesta cruda de los tres.
      Sirve de referencia al montar el cliente de la Fase 3.
- [ ] **Notificaciones** — `notifications/tools/list_changed`. ¿Se pueden
      activar? ¿Tiene sentido aquí?
- [ ] **Ciclo de vida del subproceso** — quién cierra stdin, qué pasa si el
      servidor muere, qué queda zombi en Windows. Solo medido.
- [ ] **El doble encoding, con literales** — la salida real de `get_price`, no
      una descripción de ella.
- [ ] **`mcp-qiskit` stateless, con el síntoma literal** — qué devuelve
      exactamente el `add_gate` sin circuito reenviado.
- [ ] **Recursos y prompts** — se anuncian como capacidades. ¿Los usan estos
      servidores? ¿Están vacíos?

### Fase 2

- [ ] **Escribir un server: el camino real** — desde `@mcp.tool()` hasta que
      aparece en `tools/list`. Con el JSON exacto que se intercambia.
- [ ] **Traducción de tipos → JSON Schema** — tabla completa: qué tipo de
      Python produce qué schema, y qué no tiene traducción.
- [ ] **Anatomía de una descripción buena** — el `list_tools()` del servidor
      propio junto al del financiero, comentados línea a línea. Tarea 2.9.
- [ ] **MCP Inspector** — qué se ve en el Inspector que no se ve en el cliente.
- [ ] **`outputSchema` y `structured_content` propio** — cómo declarar la
      salida para que el cliente no tenga que parsear texto.
- [ ] **Errores propios** — qué pasa si una función lanza, y cómo se devuelve
      un error de negocio legible sin romper la sesión.

### Fase 3

- [ ] **Dos servidores simultáneos** — prefijo de nombres, colisiones,
      gestión de dos procesos a la vez.
- [ ] **Coste de bytes** — cuánto pesa reenviar el dict del circuito en cada
      llamada, y si eso justifica un reducer.
- [ ] **Transporte alternativo** — HTTP/SSE o streamable. Comparar con stdio
      en latencia y complejidad. No se usa: se documenta por qué no.

### Transversal

- [ ] **Verificación de versión** — `mcp<2` en cada arranque. ¿Sigue siendo
      necesario al subir de versión? **Revisar en cada actualización.**
- [ ] **`mcp-memory-service`** — la Fase 4. Backend de embeddings, formato de
      la memoria, coste.
- [ ] **Prueba de las notas** — releer este fichero dentro de seis meses y
      marcar qué sigue siendo cierto. Un cuaderno técnico que no se revisa
      miente.
