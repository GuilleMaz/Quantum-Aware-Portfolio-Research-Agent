"""Clientes MCP — la UNICA capa que habla con servidores MCP.

Regla inviolable (``AGENTS.md`` 3.2): ninguna llamada a un servidor MCP fuera
de este paquete. Ni los agentes, ni los nodos del grafo, ni los labs (salvo los
experiments de la Fase 1, cuyo proposito es tocar el protocolo crudo).

## Diseno (decisions.md AD-0005, AD-0006)

Se usa el SDK oficial ``mcp`` v2 y un wrapper sobre ``ClientSessionGroup``:

- ``langchain-mcp-adapters`` esta ARQUIVADO y pinea ``mcp<2``.
- ``langchain.mcp.MCPAdapter`` esta en beta y corre sobre ``fastmcp`` v4, no
  sobre el SDK oficial.
- Escribir el adaptador son ~30 lineas y obliga a entender el ciclo
  ``list_tools() -> call_tool()``, que es el objetivo de aprendizaje.

## Nota importante sobre el entorno

Los procesos stdio que lanza el cliente MCP **NO heredan el entorno**. Reciben
una allow-list (``PATH``, ``USERPROFILE``, ``TEMP``... en Windows). Las API keys
**no** llegan: hay que pasarlas explicitamente con ``env=`` en
``StdioServerParameters``.

Tampoco se deben escribir ``print()`` a stdout en un servidor MCP: rompe el
protocolo JSON-RPC. A ``stderr``.
"""

from quantum_portfolio.mcp_clients.session_group import (
    MCPServerSpec,
    get_server_group,
    list_all_tools,
)

__all__ = [
    "MCPServerSpec",
    "get_server_group",
    "list_all_tools",
]