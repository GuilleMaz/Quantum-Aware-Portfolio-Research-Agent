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

# MCP — el protocolo

> **Prerrequisitos:** ninguno. **Objetivo:** entender el ciclo
> `initialize` → `list_tools` → `call_tool`, los transportes, y por qué las
> descripciones de las herramientas son contratos.

## 1. Qué es MCP

El Model Context Protocol es un estándar abierto (JSON-RPC 2.0) para exponer
**herramientas, recursos y prompts** a aplicaciones LLM. Piensa en una API web,
pero diseñada para que la consuma un modelo: el servidor **anuncia** sus
capacidades y el cliente **descubre** en tiempo de ejecución, sin código
generado ni SDK específico por servidor.

```
cliente (OpenCode, Claude Desktop, Cursor, tu grafo)
  │  JSON-RPC 2.0 sobre un transporte
  ▼
servidor (un proceso separado: financial-mcp-server, mcp-qiskit, el tuyo)
```

El mismo servidor lo usan los tres clientes sin cambios. Esa es la gracia.

## 2. El ciclo (tres mensajes, orden fijo)

```
cliente ──initialize──► servidor    ¿quién eres, qué protocolo hablas?
cliente ◄───result───── servidor    versión, capacidades, info
cliente ──tools/list─► servidor    ¿qué herramientas tienes?
cliente ◄───result───── servidor    nombre + descripción + input_schema por tool
cliente ──tools/call─► servidor    usa "get_price" con {"symbol": "AAPL"}
cliente ◄───result───── servidor    content, structured_content, is_error
```

Nada es negociado en caliente salvo la versión del protocolo. El resto es
descubrimiento puro.

## 3. Transportes

| Transporte | Cómo va | Cuándo |
|---|---|---|
| **stdio** | El cliente lanza el servidor como subproceso; hablan por stdin/stdout | Escritorio (OpenCode, Claude Desktop, Cursor). Todos los de este proyecto |
| Streamable HTTP | El servidor escucha en un puerto | Despliegue, multi-usuario |
| SSE | Eventos servidor→cliente (legacy) | Solo servidores antiguos |

**Regla de oro de stdio:** nada escribe a `stdout` salvo el protocolo. Un
`print()` de depuración en el servidor **rompe** el JSON-RPC. Los logs van a
`stderr`. (El banner ASCII de FastMCP que verás al arrancar `mcp-qiskit` va a
`stderr` a propósito.)

## 4. Las descripciones son contratos

El LLM no ve tu código. Ve: nombre, descripción y `input_schema` (JSON Schema).
Con **solo eso** decide si llama a tu herramienta y con qué argumentos.

```{code-cell} ipython3
# Qué ve el modelo por cada herramienta (esquema simplificado).
tool_vista_por_el_modelo = {
    "name": "get_momentum",
    "description": "Get momentum signals: 30d/90d price momentum, volatility, ...",
    "input_schema": {
        "type": "object",
        "properties": {"symbol": {"type": "string"}},
        "required": ["symbol"],
    },
}
print(tool_vista_por_el_modelo["description"])
```

Por eso `get_momentum` trae la volatilidad en la misma llamada y lo anuncia:
un buen modelo lo detecta y ahorra una llamada. En la Fase 2 lo sufrirás al
revés: si tu `loan_emi` no se describe bien, el modelo no la elige.

## 5. Resultados: tres campos

- `content`: lista de bloques (texto, imagen, recurso). **Es lo que lee el modelo.**
- `structured_content`: el retorno como JSON contra el `output_schema`.
- `is_error`: `True` si la herramienta falló. **No lanza excepción**: el error
  vuelve como resultado normal para que el modelo lo corrija.

Dos trampas verificadas de los servidores de este proyecto:

1. `financial-mcp-server` devuelve `{"result": "<json string>"}`: un JSON
   **serializado dentro de un string**. Hay que parsear dos veces.
2. Un retorno escalar se envuelve: `structured_content == {"result": 42}`,
   no `42` pelado.

## 6. El hijo no hereda tu entorno

El proceso stdio recibe una allow-list (en Windows: `PATH`, `USERPROFILE`,
`TEMP`, ...). **Tus API keys no llegan.** Se pasan explícitas con `env=`:

```python
StdioServerParameters(
    command="uvx",
    args=["--from", "financial-mcp-server", "--with", "mcp<2", "financial-mcp"],
    env={"FRED_API_KEY": "..."},
)
```

## 7. La trampa de los dos servidores externos

Ambos declaran `mcp[cli]>=1.0.0` **sin cota superior**. uv instala MCP 2.x,
donde `FastMCP` fue renombrado a `MCPServer` y `mcp.server.fastmcp` no existe:

```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'
```

El pin `--with "mcp<2"` es obligatorio y no aparece en ninguna documentación
upstream. Está en `config/mcp_servers.json`, que es la fuente única de verdad.

## Ejercicios

<details><summary>1. ¿Por qué un print() a stdout rompe stdio?</summary>
Porque stdout es el canal del protocolo. El cliente parsea cada línea como
JSON-RPC; un log intercalado corrompe el stream. Por eso existe stderr.
</details>

<details><summary>2. ¿Qué ve el modelo de tu herramienta?</summary>
Solo nombre, descripción y esquema de entrada. Ni el código, ni los tipos
internos, ni tus comentarios. Si la descripción no dice que trae volatilidad,
el modelo pedirá otra herramienta para la volatilidad.
</details>

## Referencias

- Spec MCP: https://modelcontextprotocol.io/ (verificada)
- SDK Python v2, README: https://github.com/modelcontextprotocol/python-sdk (verificada)
- Docs del SDK: https://py.sdk.modelcontextprotocol.io/ (verificada)
