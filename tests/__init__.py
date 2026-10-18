"""Tests del paquete ``src/quantum_portfolio/``.

Reglas (``AGENTS.md`` 3.4):

- Todo cambio en ``src/`` requiere test. Sin excepcion.
- Los tests de ``labs/`` no viven aqui: los experiments no se testean.
- Los tests que necesiten servidores MCP externos se marcan::

      @pytest.mark.integration

  y se excluyen por defecto con ``uv run pytest -m "not integration"``.
"""

__all__: list[str] = []
