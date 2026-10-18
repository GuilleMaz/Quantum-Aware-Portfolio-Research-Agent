# ADR 0003 — uv como gestor único, Python 3.12

- **Estado:** aceptado
- **Fecha:** 2026-10-18

## Contexto

El proyecto combina dependencias con perfiles de compatibilidad distintos
(Qiskit con pin exacto, LangGraph, MCP SDK v2) y necesita lanzar servidores MCP
externos sin contaminar el entorno del proyecto. El sistema trae Python 3.13.5.

## Decisión

- **uv** como único gestor: `uv sync`, `uv run`, `uv add`, `uvx` para los
  servidores MCP externos.
- **Python 3.12**, fijado en `.python-version`. uv lo instala automáticamente
  si falta.
- Los servidores MCP externos se lanzan con `uvx` (entornos aislados por
  servidor), nunca instalados en el `.venv` del proyecto.

## Consecuencias

- Un solo lockfile, entornos reproducibles.
- `mcp-qiskit` (con su pin duro `qiskit==2.3.1` y sus ~97 paquetes) queda
  aislado: no puede romper las dependencias del proyecto.
- Los comandos de arranque llevan sus propios pins (`--with "mcp<2"`,
  `--from "mcp-qiskit[mcp]"`) documentados en `config/mcp_servers.json`.

## Alternativas

- **venv + pip clásico:** más simple de leer para aprender Python, pero sin
  lockfile y con los servidores MCP instalados a mano.
- **Python 3.13 del sistema:** más nuevo, pero Qiskit y LangChain juntos son
  propensos a conflictos en la versión más reciente.
- **venv manual separado para Qiskit:** aislamiento equivalente, pero dos
  entornos que mantener a mano en vez de uno gestionado por uv.
