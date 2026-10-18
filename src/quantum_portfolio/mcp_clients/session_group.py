"""Wrapper sobre ``ClientSessionGroup`` del MCP SDK v2.

Se implementa en la **Fase 3** (tarea 3.1). Aqui solo queda el contrato de la
interfaz, fijada contra la API real verificada del SDK v2.3.0.

## Por que ClientSessionGroup

``ClientSessionGroup`` fusiona las herramientas de N servidores MCP en un solo
namespace y da proteccion de colisiones de nombres gratis:

- Si dos servidores exponen una tool con el mismo nombre, lanza ``MCPError``
  en vez de sobrescribir silenciosamente.
- ``component_name_hook`` reescribe la clave del dict (el nombre del wire no
  cambia) y aplica a TODOS los nombres, no solo a los conflictivos.

Eso es justo lo que necesita un grafo que consume simultaneamente el servidor
financiero y el cuantico.

## Estado actual

Estado de implementacion: **PENDIENTE** (Fase 3, tarea 3.1).

La interfaz objetivo, ya verificada contra la API real:

```python
from mcp import ClientSessionGroup, StdioServerParameters

async with ClientSessionGroup(
    component_name_hook=lambda name, info: f"{info.name}.{name}"
) as group:
    await group.connect_to_server(StdioServerParameters(command="uvx", args=[...]))
    group.tools          # dict[str, Tool] con todos los servidores fusionados
    await group.call_tool("financial.get_price", {"symbol": "AAPL"})
```

## Notas de la API v2 que ya se saben (verificadas)

- ``Client`` es un dataclass: construirlo NO abre nada. Todo el ciclo de vida
  ocurre dentro de ``async with``; fuera del bloque da ``RuntimeError``.
- El cliente no es reutilizable tras salir del bloque ``async with``.
- Los errores de herramienta **NO lanzan excepcion**: vuelven con
  ``is_error=True`` en el resultado.
- ``structured_content`` envuelve los escalares: ``{"result": 42}``, no ``42``.
- ``read_timeout_seconds`` es un ``float`` en segundos (en v1 era ``timedelta``).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp import ClientSessionGroup
    from mcp.types import Tool

#: Fichero de configuracion con los comandos de los servidores MCP.
#: Es la fuente unica de verdad (``AGENTS.md`` 3.3). No se hardcodean comandos.
DEFAULT_SERVERS_CONFIG = Path(__file__).resolve().parents[3] / "config" / "mcp_servers.json"


@dataclass(frozen=True)
class MCPServerSpec:
    """Especificacion de un servidor MCP.

    Mapea 1:1 con los campos de ``StdioServerParameters`` del SDK v2, mas el
    prefijo que usaremos para evitar colisiones de nombres entre servidores.
    """

    name: str
    command: str
    args: tuple[str, ...] = ()
    env: dict[str, str] | None = None
    cwd: str | None = None
    timeout_seconds: float = 60.0

    def to_stdio_params(self) -> Any:
        """Convierte a ``StdioServerParameters`` del SDK.

        PENDIENTE (Fase 3, tarea 3.1). La firma de ``env`` es
        ``dict[str, str] | None``.
        """
        from mcp import StdioServerParameters

        return StdioServerParameters(
            command=self.command,
            args=list(self.args),
            env=self.env,
            cwd=self.cwd,
        )


def load_server_specs(config_path: Path | None = None) -> list[MCPServerSpec]:
    """Carga los specs desde ``config/mcp_servers.json``.

    PENDIENTE (Fase 3, tarea 3.1).
    """
    raise NotImplementedError("Se implementa en la Fase 3, tarea 3.1.")


def get_server_group(specs: list[MCPServerSpec]) -> ClientSessionGroup:
    """Construye un ``ClientSessionGroup`` con todos los servidores.

    PENDIENTE (Fase 3, tarea 3.1).
    """
    raise NotImplementedError("Se implementa en la Fase 3, tarea 3.1.")


async def list_all_tools(group: ClientSessionGroup) -> dict[str, Tool]:
    """Devuelve el dict de herramientas fusionado por todos los servidores.

    Los nombres llevan prefijo por servidor, p.ej. ``"financial.get_price"``.

    PENDIENTE (Fase 3, tarea 3.2).
    """
    raise NotImplementedError("Se implementa en la Fase 3, tarea 3.2.")


__all__ = [
    "DEFAULT_SERVERS_CONFIG",
    "MCPServerSpec",
    "get_server_group",
    "list_all_tools",
    "load_server_specs",
]