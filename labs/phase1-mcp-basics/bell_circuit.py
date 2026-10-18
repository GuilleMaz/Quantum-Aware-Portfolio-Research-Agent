"""Circuito de Bell via mcp-qiskit, reenviando el dict del circuito en cada llamada."""

import asyncio
import json

from common import dump_json, qiskit_params


def payload(result):
    sc = getattr(result, "structured_content", None)
    if isinstance(sc, dict):
        if list(sc.keys()) == ["result"]:
            inner = sc["result"]
            if isinstance(inner, str):
                try:
                    return json.loads(inner)
                except Exception:
                    return inner
            return inner
        return sc
    for block in getattr(result, "content", []) or []:
        if hasattr(block, "text"):
            try:
                return json.loads(block.text)
            except Exception:
                return block.text
    return None


async def main():
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client

    async with stdio_client(qiskit_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            c = payload(await session.call_tool(
                "create_quantum_circuit_tool",
                {"num_qubits": 2, "num_classical_bits": 2},
            ))
            print("created circuit keys:", list(c.keys()) if isinstance(c, dict) else type(c))

            c = payload(await session.call_tool(
                "add_gate_tool",
                {"circuit": c, "gate_name": "h", "qubits": [0]},
            ))
            c = payload(await session.call_tool(
                "add_gate_tool",
                {"circuit": c, "gate_name": "cx", "qubits": [0, 1]},
            ))
            c = payload(await session.call_tool(
                "add_measurement_tool",
                {"circuit": c, "qubits": [0, 1], "clbits": [0, 1]},
            ))

            run = payload(await session.call_tool(
                "run_circuit_tool",
                {"circuit": c, "backend_name": "aer_simulator", "shots": 1024},
            ))
            print("RUN RESULT:")
            print(json.dumps(run, indent=2, ensure_ascii=False, default=str)[:4000])

            # Normalizar counts
            counts = None
            if isinstance(run, dict):
                for key in ("counts", "result", "measurement_counts", "data"):
                    if key in run:
                        val = run[key]
                        if isinstance(val, dict):
                            counts = val
                            break
                        if isinstance(val, str):
                            try:
                                counts = json.loads(val)
                                break
                            except Exception:
                                pass
                if counts is None:
                    # buscar cualquier dict con claves tipo "00"
                    for v in run.values():
                        if isinstance(v, dict) and all(isinstance(k, str) and set(k) <= {"0", "1"} for k in v):
                            counts = v
                            break

            out = {
                "counts": counts,
                "shots": 1024,
                "raw": run,
            }
            dump_json("bell_circuit.json", out)
            print("counts =", counts)


asyncio.run(main())
