# Fase 2 — Tu primer MCP server

## 📖 Lee antes de empezar

| Notebook | Qué te da |
|---|---|
| [`theory/python-sdk.md`](../../theory/python-sdk.md) | `MCPServer` v2, tipos → JSON Schema, docstrings como contrato |
| [`theory/mcp.md`](../../theory/mcp.md) | El protocolo, por si quieres ver los mensajes en crudo |

> Depende de cerrar la Fase 1. Si no entiendes `list_tools()` → `call_tool()`
> como cliente, escribir un servidor no significa nada.

---

## Objetivo de aprendizaje

Comprender que un MCP server es **un proceso separado** que escribe sus
capacidades al arrancar, y que **la descripción de una herramienta es lo único
que el LLM tiene para decidir si la usa**. Escribirla bien no es documentación:
es diseño de interfaz.

---

## Qué construyes

Un servidor MCP de finanzas con 3 herramientas:

| Herramienta | Qué hace |
|---|---|
| `compound_interest` | Capital final dado principal, tasa y periodos |
| `loan_emi` | Cuota de un préstamo con amortización francesa |
| `npv` | Valor presente de un flujo de caja |

**No accede a datos reales.** La idea es entender el protocolo, no construir un
producto.

---

## Tareas

- [ ] 2.1 Crear `pyproject.toml` con `mcp>=2.3.0`
- [ ] 2.2 `compound_interest(principal, rate, periods)` con anotaciones de tipo.
      **Comprueba que el tipo ES el JSON Schema** (mira `tools/list` en el Inspector).
- [ ] 2.3 `loan_emi(principal, annual_rate, years)` con amortización francesa
- [ ] 2.4 `npv(rate, cashflows)`
- [ ] 2.5 Tests unitarios (casos límite: 0 años, tasa 0, lista de flujos vacía)
- [ ] 2.6 `uv run mcp dev server.py` → abrir MCP Inspector
- [ ] 2.7 Conectar a OpenCode
- [ ] 2.8 **🟢 Prueba de contrato de diseño** (abajo)
- [ ] 2.9 Comparar tu `tools/list` con el del servidor financiero (42 tools).
      ¿Qué hacen las descripciones buenas? → `../../docs/mcp-notes.md`
- [ ] 2.10 Cerrar la fase y promover a `src/`

---

## 🟢 La prueba que importa

Abre el LLM de tu cliente y pide, **sin mencionar ninguna herramienta**:

> "¿Cuánto pago al mes por un coche de 20.000€ al 8% a 5 años?"

El LLM debe elegir `loan_emi` por su cuenta.

- **Si lo hace** → tu descripción funciona.
- **Si hay que nombrarla** → la descripción está mal. Vuelve a escribirla.

Esto es `description` como contrato, y es **lo único que importa** cuando
trabajas con LLMs. En la Fase 1 lo viste con las 42 tools del servidor
financiero: `get_momentum` trae la volatilidad en la misma llamada, y eso se
anuncia en el nombre y la descripción. Un buen LLM lo detecta y lo usa.

---

## API del SDK v2 (verificada)

```python
from mcp.server import MCPServer

mcp = MCPServer("FinanceMini", instructions="...")


@mcp.tool(title="Cuota de préstamo")
def loan_emi(principal: float, annual_rate: float, years: int) -> float:
    """Calcula la cuota mensual de un préstamo con amortización francesa.

    Args:
        principal: Capital prestado en euros.
        annual_rate: Tipo de interés anual en decimal (0.08 = 8%).
        years: Plazo en años.

    Returns:
        La cuota mensual en euros.
    """
    ...
```

**Lo que no escribes** (y por eso MCP es interesante): JSON Schema (los tipos de
Python **son** el schema), parseo de peticiones, validación, ni manejo del
protocolo.

Dos funciones tipadas y un docstring. Eso es todo.

### Cambios respecto a la v1 (migración)

```python
# v1 (lo que verás en todos los tutoriales)
from mcp.server.fastmcp import FastMCP

# v2 (actual)
from mcp.server import MCPServer
```

**No hay alias legacy.** `mcp.server.fastmcp` lanza `ModuleNotFoundError`.

### Ejecutar y depurar

```bash
uv run mcp dev server.py              # servidor con recarga + Inspector
uv run mcp run server.py --transport streamable-http
```

---

## ✅ Criterio de cierre

El LLM elige la herramienta correcta sin que se la nombres.

---

## Convenciones

Igual que Fase 1: cuaderno. Pero esta vez tiene `src/` propio y **tests de
verdad** — es código que se promueve al final.

Al promover, remember: la lógica de MCP va a
`src/quantum_portfolio/mcp_clients/`, nunca dentro del server.