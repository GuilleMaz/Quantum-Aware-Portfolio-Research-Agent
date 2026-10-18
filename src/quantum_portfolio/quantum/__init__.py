"""Motor cuantico — QAOA y simulacion.

**Usa Qiskit DIRECTO, no el servidor MCP** (decisions.md AD-0008). El servidor
``mcp-qiskit`` sirve para aprender el protocolo (Fase 1) y para demostrar la
integracion multi-MCP (Fase 3), pero no como motor por sus bugs verificados:

- ``statevector`` se devuelve como strings, no como numeros JSON.
- ``run_circuit`` degrada en silencio a un simulador generico si el backend no
  existe (falsa simulacion).
- Los gates parametricos sin ``params`` reciben defaults silenciosos
  (``rx``->0.5): circuitos incorrectos sin error.
- No hay simuladores ruidosos reales ni acceso a hardware IBM.

## Dependencias

```powershell
uv sync --extra quantum    # qiskit + qiskit-aer + matplotlib
```

## Nota sobre qiskit-optimization

`qiskit-optimization` esta **descontinuado por IBM**. Las matrices QUBO se
construyen a mano con numpy, lo que ademas es pedagogicamente mejor.

## Se implementa en la Fase 3

- ``qubo.py`` — construir C desde la matriz de covarianza
- ``qaoa.py`` — mapeo Ising, Hamiltonian de coste, ansatz
- ``simulator.py`` — ejecucion en Aer, con y sin ruido
"""

__all__: list[str] = []