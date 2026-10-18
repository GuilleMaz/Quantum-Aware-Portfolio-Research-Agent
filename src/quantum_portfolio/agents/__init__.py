"""Agentes del sistema.

Se implementan en la **Fase 3**. Cada agente se corresponde con un nodo del
grafo y su unica via de obtener datos es ``quantum_portfolio.mcp_clients``
(regla ``AGENTS.md`` 3.2).

## Agentes

- ``financial_analyst.py`` — universo de candidatos + metricas de riesgo/retorno.
  Consume ``scan_universe`` (batch, 1 llamada), ``get_momentum`` (trae
  volatilidad en la MISMA llamada que el momentum) y ``get_fundamentals``.
  Fija ``alta_volatilidad``, que decide el routing.

- ``quantum_researcher.py`` — formula el problema de optimizacion como circuito
  QAOA. Construye el QUBO a mano con numpy (qiskit-optimization esta
  descontinuado) y ejecuta con **Qiskit directo**, no con el MCP.

  **Trampa critica:** el server MCP cuántico es stateless, asi que hay que
  reenviar el dict del circuito en cada tool call. En el grafo eso lo resuelve
  el reducer de ``state.py``. Si prometes pasarlo al motor Qiskit directo,
  recuerda que ahi el estado SI lo mantiene el objeto ``QuantumCircuit``.

- ``memory.py`` — memoria persistente entre sesiones (Fase 4).
"""

__all__: list[str] = []