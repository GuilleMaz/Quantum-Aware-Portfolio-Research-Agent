"""Demuestra que mcp-qiskit es stateless: si no reenvias el dict, se pierde el estado."""

import asyncio
import json

from common import dump_json, qiskit_params


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

            c0 = payload(await session.call_tool(
                "create_quantum_circuit_tool", {"num_qubits": 2, "num_classical_bits": 2}
            ))

            # Correcto: reenviamos c0, recibimos c1 con la H.
            c1 = payload(await session.call_tool(
                "add_gate_tool", {"circuit": c0, "gate_name": "h", "qubits": [0]}
            ))

            # OLVIDO: no reenviamos el circuito. El servidor crea uno nuevo (8 qubits por defecto)
            # y anade cx ahi. El c1 original (con H) se pierde.
            c_forgotten = payload(await session.call_tool(
                "add_gate_tool", {"circuit": None, "gate_name": "cx", "qubits": [0, 1]}
            ))

            out = {
                "circuit_after_h_keys": list(c1.keys()) if isinstance(c1, dict) else str(type(c1)),
                "circuit_forgotten_keys": list(c_forgotten.keys()) if isinstance(c_forgotten, dict) else str(type(c_forgotten)),
                "circuit_after_h": c1,
                "circuit_forgotten": c_forgotten,
                "conclusion": (
                    "El segundo add_gate sin reenviar el dict NO modifica c1: el servidor es stateless. "
                    "El circuito devuelto es uno nuevo (8 qubits por defecto) con solo cx, sin la H."
                ),
            }
            dump_json("stateless_demo.json", out)
            print(json.dumps({k: out[k] for k in ("circuit_after_h_keys", "circuit_forgotten_keys", "conclusion")}, indent=2, ensure_ascii=False))


asyncio.run(main())
