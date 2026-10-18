"""Dibuja un circuito de Bell en ascii. Requiere PYTHONIOENCODING=utf-8 en Windows."""

import asyncio
import json
import os

from common import qiskit_params

# Forzar UTF-8 en la salida de este proceso (defensa en profundidad).
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def payload(result):
    sc = getattr(result, "structured_content", None)
    if isinstance(sc, dict) and list(sc.keys()) == ["result"]:
        inner = sc["result"]
        if isinstance(inner, str):
            try:
                return json.loads(inner)
            except Exception:
                return inner
        return inner
    return sc


async def main():
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client

    async with stdio_client(qiskit_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            c = payload(await session.call_tool(
                "create_quantum_circuit_tool", {"num_qubits": 2, "num_classical_bits": 2}
            ))
            c = payload(await session.call_tool(
                "add_gate_tool", {"circuit": c, "gate_name": "h", "qubits": [0]}
            ))
            c = payload(await session.call_tool(
                "add_gate_tool", {"circuit": c, "gate_name": "cx", "qubits": [0, 1]}
            ))
            c = payload(await session.call_tool(
                "add_measurement_tool", {"circuit": c, "qubits": [0, 1], "clbits": [0, 1]}
            ))

            drawn = payload(await session.call_tool(
                "draw_circuit_tool", {"circuit": c, "output_format": "ascii"}
            ))
            text = drawn if isinstance(drawn, str) else json.dumps(drawn, ensure_ascii=False)
            print(text)
            # Guardar tambien a fichero con UTF-8
            out_path = os.path.join(os.path.dirname(__file__), "snapshots", "bell_circuit_ascii.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print("\nsaved", out_path)


asyncio.run(main())
