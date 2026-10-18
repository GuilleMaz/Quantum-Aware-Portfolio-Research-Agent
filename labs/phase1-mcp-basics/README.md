# Fase 1 — Fundamentos de MCP

## 📖 Lee antes de empezar

| Notebook | Qué te da |
|---|---|
| [`theory/mcp.md`](../../theory/mcp.md) | El protocolo: JSON-RPC, transportes, el ciclo `list_tools()` → `call_tool()` |
| [`theory/tool-discovery.md`](../../theory/tool-discovery.md) | Cómo el LLM decide qué herramienta usar |
| [`theory/qiskit-basics.md`](../../theory/qiskit-basics.md) | Compuertas, estado de Bell, ejecución en Aer |

---

## Objetivo de aprendizaje

Entender el ciclo `list_tools()` → `call_tool()`, y que **MCP estandariza la
interfaz**. Ver que un servidor MCP es **un proceso separado** que anuncia sus
capacidades, y que las descripciones de las herramientas son **contratos para el
LLM**, no documentación decorativa.

Esta fase **no construye nada reutilizable**. El código se tira. Lo que se
queda es la comprensión del protocolo.

---

## ⚠️ Antes de ejecutar nada

Los dos servidores externos están **rotos** con MCP 2.x. Ninguna documentación
upstream lo menciona. Verificado:

```bash
uvx financial-mcp-server          # ❌ no existe ese ejecutable
uvx --from financial-mcp-server financial-mcp
                                  # ❌ ModuleNotFoundError: mcp.server.fastmcp
```

Los comandos correctos:

```bash
uvx --from financial-mcp-server --with "mcp<2" financial-mcp
uvx --from "mcp-qiskit[mcp]" mcp-qiskit
```

**Paciencia con el cuántico: 67 s el primer arranque** (descarga 97 paquetes).
Después ~9 s.

---

## Tareas

### 1.A — Servidor financiero
- [ ] 1.1 `uv sync` y comprobar que el venv arranca
- [ ] 1.2 Handshake `initialize` **a mano**, sin librería (ver `theory/mcp.md`)
- [ ] 1.3 `list_tools.py` → `snapshots/financial_tools.json` (**42** tools, no 14)
- [ ] 1.4 `get_price("AAPL")` → guardar salida real
- [ ] 1.5 `get_fundamentals("AAPL")` → guardar salida real
- [ ] 1.6 `get_momentum("AAPL")` → trae **volatilidad** en la misma llamada → guardar
- [ ] 1.7 Parsear el doble encoding `{"result": "<json string>"}` → anotar en
      [`../../docs/mcp-notes.md`](../../docs/mcp-notes.md)

### 1.B — Servidor cuántico
- [ ] 1.8 Lanzar `uvx --from "mcp-qiskit[mcp]" mcp-qiskit`
- [ ] 1.9 `list_tools()` → 13 tools → `snapshots/qiskit_tools.json`
- [ ] 1.10 `bell_circuit.py`: `create` → `h` → `cx` → `measure` → `run(1024)`
- [ ] 1.11 Verificar `{"00": ~512, "11": ~512, "01": ~0, "10": ~0}` →
      `snapshots/bell_circuit.json`
- [ ] 1.12 **🔴 Descubrir que es stateless**: olvidar reenviar el dict del
      circuito en el segundo `add_gate` y observar qué pasa →
      `../../docs/mcp-notes.md`
- [ ] 1.13 **🔴 Reproducir el fallo silencioso**: `rx` sin `params` y comprobar
      que el circuito queda mal **sin error**
- [ ] 1.14 `draw_circuit_tool("ascii")` con `PYTHONIOENCODING=utf-8`

### 1.C — Integración con el LLM
- [ ] 1.15 Claude Desktop: copiar `config/clients/claude_desktop_config.example.json`
      a `%APPDATA%\Claude\claude_desktop_config.json` (**ruta absoluta** a `uvx.exe`)
- [ ] 1.16 OpenCode: `opencode.json` ya está en la raíz. Verificar con **`/mcps`**
- [ ] 1.17 Pedir un análisis de ticker **sin nombrar las herramientas**
- [ ] 1.18 Pedir un circuito de Bell. ¿Recuerda reenviar el circuito?
- [ ] 1.19 Cerrar la fase: promover a `src/`, actualizar `project-memory/`

---

## 🔴 Las dos tareas que importan

**1.12 y 1.13** son las que hacen que esta fase valga la pena. Son bugs reales
de `mcp-qiskit`, y los dos hacen lo mismo: **fallan en silencio**. El circuito
no lanza excepción, el agente cree que funcionó, y el resultado es basura.

Si las haces bien, entiendes por qué la Fase 3 necesita un reducer de estado, y
por qué el motor cuántico real va a ser Qiskit directo (`AGENTS.md` §8).

---

## ✅ Criterio de cierre

`snapshots/bell_circuit.json` con distribución de Bell correcta ±5%:

```json
{ "counts": { "00": 522, "11": 502 }, "shots": 1024 }
```

---

## Snapshots

Las salidas reales se commitean en `snapshots/`. Son la **evidencia** de que
las herramientas funcionan, y las necesitarás en la Fase 3 para construir tests
sin llamar a la red.

## Convenciones de esta carpeta

Es **cuaderno**, no producto:
- Ruff con reglas relajadas (`pyproject.toml` lo ignora).
- Sin type hints obligatorios.
- Comenta lo que te sorprende, sobre todo lo que no funciona.
- Al cerrar la fase, se congela. No se toca más.