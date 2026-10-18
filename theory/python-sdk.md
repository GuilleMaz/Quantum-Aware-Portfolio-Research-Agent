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

# Python SDK — escribir un servidor (v2)

> **Prerrequisitos:** `mcp.md`. **Objetivo:** escribir un servidor MCP con
> el SDK oficial v2 y entender que los tipos de Python **son** el JSON Schema.

## 1. Un servidor en 15 líneas

```python
from mcp.server import MCPServer

mcp = MCPServer("FinanceMini", instructions="...")


@mcp.tool(title="Cuota de préstamo")
def loan_emi(principal: float, annual_rate: float, years: int) -> float:
    """Calcula la cuota mensual de un préstamo con amortización francesa."""
    ...
```

Lo que **no** escribiste: JSON Schema (`principal: float` **es** el schema),
parseo de peticiones, validación ni manejo del protocolo. Dos funciones tipadas
y un docstring. Eso es todo.

```{code-cell} ipython3
# La intuición sin servidor: los tipos generan el esquema.
import inspect

def loan_emi(principal: float, annual_rate: float, years: int) -> float:
    """Calcula la cuota mensual de un préstamo con amortización francesa."""
    r = annual_rate / 12
    n = years * 12
    return principal * r / (1 - (1 + r) ** -n)

print(inspect.signature(loan_emi))
print(f"cuota 20000€ al 8% a 5 años: {loan_emi(20000, 0.08, 5):.2f} €/mes")
```

## 2. Migración v1 → v2

```python
# v1 (lo que verás en todos los tutoriales antiguos)
from mcp.server.fastmcp import FastMCP

# v2 (actual, verificada en mcp 2.3.0)
from mcp.server import MCPServer
```

**No hay alias legacy.** `mcp.server.fastmcp` lanza `ModuleNotFoundError`.
También cambiaron: `McpError` → `MCPError`, campos camelCase → snake_case
(`structuredContent` → `structured_content`), y `read_timeout_seconds` ahora es
`float` en segundos (antes `timedelta`).

## 3. El docstring es el contrato

El modelo solo ve el docstring (más tipos). Convención que funciona:

- Primera línea: qué hace, con las palabras del usuario.
- `Args:`: cada parámetro con unidades y formato (`0.08 = 8%`, no "tasa").
- `Returns:`: qué devuelve, con unidades.

Si el usuario dice "coche" y tu docstring dice "préstamo con amortización
francesa", el modelo conecta. Si dice "EMI" sin más, no.

## 4. Ejecutar y depurar

```bash
uv run mcp dev server.py                 # servidor + Inspector
uv run mcp run server.py --transport streamable-http
```

## Ejercicios

<details><summary>1. ¿Qué pasa si anotas shares: str en vez de int?</summary>
El esquema dirá string; el modelo pasará "10"; tu código recibirá "10" y la
aritmética fallará o, peor, concatenará. Los tipos son el esquema: un tipo mal
es un contrato mal.
</details>

<details><summary>2. ¿Dónde van los logs del servidor?</summary>
A stderr. Stdout es el canal del protocolo y un print lo rompe.
</details>

## Referencias

- README del SDK con los snippets: https://github.com/modelcontextprotocol/python-sdk (verificada)
- Docs: https://py.sdk.modelcontextprotocol.io/ (verificada)
