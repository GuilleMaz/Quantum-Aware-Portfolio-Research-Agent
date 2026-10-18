"""Quantum-Aware Portfolio Research Agent.

Sistema multi-agente que combina analisis financiero con optimizacion cuantica
(QAOA) para explorar estrategias de cartera.

Nota de arquitectura (ver ``project-memory/decisions.md`` AD-0008): el motor
cuantico es Qiskit DIRECTO, no el servidor MCP. El MCP es la capa de
orquestacion; los servidores externos se usan para aprender el protocolo.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]