# Configuración de clientes MCP

Los tres servidores MCP del proyecto, traducidos a la sintaxis de cada cliente.

**Los tres clientes tienen sintaxis distintas y no compatibles entre sí.** No
intentes copiar un fichero a otro cliente.

---

## Los ficheros

| Fichero | Cliente | Copiar a |
|---|---|---|
| `opencode.example.json` | OpenCode | `opencode.json` en la raíz del repo |
| `claude_desktop_config.example.json` | Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` |
| `cursor.example.json` | Cursor | `.cursor/mcp.json` |

**Nota:** `claude_desktop_config.example.json` y `cursor.example.json` son JSON
puro, **sin comentarios** — ambos clientes fallan al parsear si hay `//`. La
explicación está aquí y en las claves `"//"` de los que sí las admiten.

---

## Tabla de sintaxis

| | OpenCode | Claude Desktop | Cursor |
|---|---|---|---|
| Clave raíz | `mcp` | `mcpServers` | `mcpServers` |
| `type` para stdio | **`"local"`** | **no existe** | **`"stdio"`** obligatorio |
| `command` | **array** `["uvx", ...]` | string + `args` | string + `args` |
| Vars de entorno | `{env:VAR}` | sin soporte | `${env:VAR}` (con `$`) |
| `envFile` | no | no | **sí** |
| Recarga | **automática al guardar** | reiniciar la app | reiniciar |
| Slash command | **`/mcps`** | — | — |

**En OpenCode `type: "stdio"` es inválido** — el schema JSON solo admite
`"local"` y `"remote"`, y rechaza el fichero si lo pones. En Cursor es
**obligatorio** sin él.

---

## ⚠️ Ruta absoluta a `uvx.exe` — obligatoria en Windows

```
C:\Users\<tu-usuario>\.local\bin\uvx.exe
```

Verificado: los clientes GUI (Claude Desktop, Cursor) se lanzan desde el menú de
Inicio con un `PATH` mínimo. En ese contexto `uvx` da `NOT FOUND`. Con la ruta
absoluta, el servidor arranca sin problema.

En OpenCode `command` es un array (no hay shell), pero mantenemos la ruta
absoluta por consistencia y por si algún cliente cambia su resolución.

---

## Los tres comandos (verificados ejecutando)

```bash
uvx --from financial-mcp-server --with "mcp<2" financial-mcp
uvx --from "mcp-qiskit[mcp]" mcp-qiskit
uvx --from mcp-memory-service memory server
```

### Por qué `--with "mcp<2"` en el servidor financiero

`financial-mcp-server` declara `mcp[cli]>=1.0.0` **sin cota superior**. uv
instala MCP 2.x, donde `FastMCP` fue renombrado a `MCPServer` y
`mcp.server.fastmcp` ya no existe:

```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'
```

**Ninguna documentación upstream menciona este pin.** Sin él, el servidor no
arranca. Lo mismo aplica a `mem0-mcp-server`.

### Por qué `--from "mcp-qiskit[mcp]"` en el cuántico

`fastmcp` está **solo en el extra `mcp`**, no en las dependencias base. Sin el
extra:

```
ModuleNotFoundError: No module named 'fastmcp'
```

El README del repo dice `command: "mcp-qiskit"` a secas, lo cual **falla**.

---

## Timeouts

`mcp-qiskit` tarda **67 s en el primer arranque** (descarga 97 paquetes) y ~9 s
en caliente. El default de OpenCode es `timeout: 5000` ms — insuficiente.

Por eso los tres servidores llevan `timeout: 60000` en la config de OpenCode.
Claude Desktop y Cursor no exponen ese ajuste; sube el timeout del sistema si
el primer arranque falla.

---

## Para OpenCode

`opencode.json` **ya está en la raíz del repo** y funciona tal cual.

```powershell
# Verifica que los servidores están cargados
# (en OpenCode)
/mcps
```

OpenCode **recarga los MCP automáticamente al guardar el config** — no hace
falta reiniciar.

---

## Para Claude Desktop

1. Copia `claude_desktop_config.example.json` a
   `%APPDATA%\Claude\claude_desktop_config.json`
2. Sustituye `C:\Users\guill\...` por tu ruta real de `uvx.exe`
3. Deja `FRED_API_KEY` vacía si no la tienes (solo afecta a 4 tools de macro)
4. **Cierra Claude Desktop por completo** (Quit, no cerrar ventana)
5. Logs en `%APPDATA%\Claude\logs\mcp.log`

**Trampa documentada por Anthropic:** si los logs muestran `${APPDATA}` sin
expandir, añade `"APPDATA": "C:\\Users\\tu_usuario\\AppData\\Roaming\\"` al
bloque `env` del servidor afectado.

---

## Para Cursor

1. Crea `.cursor/mcp.json` con el contenido de `cursor.example.json`
2. Sustituye la ruta de `uvx.exe`
3. Cursor lee `.env` de la raíz automáticamente vía `envFile`

---

## Seguridad

- **Ninguna API key se commitea.** `.env` está en `.gitignore`.
- Estos ficheros son **ejemplos**: las claves van como placeholders
  (`PEGA_AQUI_...`) o como `{env:VAR}` / `${env:VAR}`, nunca con el valor real.
- `FRED_API_KEY` es opcional y gratuita:
  https://fred.stlouisfed.org/docs/api/api_key.html
- `IBM_QUANTUM_TOKEN` es inútil hoy: los backends de IBM no son alcanzables
  desde `mcp-qiskit` (bug verificado).