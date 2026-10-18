"""Reproduce el fallo silencioso: rx sin params recibe default 0.5 sin error."""

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

            # Circuito con rx SIN params (deberia fallar, pero no falla)
            c_no = payload(await session.call_tool(
                "create_quantum_circuit_tool", {"num_qubits": 1, "num_classical_bits": 1}
            ))
            c_no = payload(await session.call_tool(
                "add_gate_tool", {"circuit": c_no, "gate_name": "rx", "qubits": [0]}
            ))
            c_no = payload(await session.call_tool(
                "add_measurement_tool", {"circuit": c_no, "qubits": [0], "clbits": [0]}
            ))

            # Circuito con rx CON params explicitos (1.0 rad) para comparar
            c_yes = payload(await session.call_tool(
                "create_quantum_circuit_tool", {"num_qubits": 1, "num_classical_bits": 1}
            ))
            c_yes = payload(await session.call_tool(
                "add_gate_tool", {"circuit": c_yes, "gate_name": "rx", "qubits": [0], "params": [1.0]}
            ))
            c_yes = payload(await session.call_tool(
                "add_measurement_tool", {"circuit": c_yes, "qubits": [0], "clbits": [0]}
            ))

            run_no = payload(await session.call_tool(
                "run_circuit_tool", {"circuit": c_no, "backend_name": "aer_simulator", "shots": 1024, "seed": 7}
            ))
            run_yes = payload(await session.call_tool(
                "run_circuit_tool", {"circuit": c_yes, "backend_name": "aer_simulator", "shots": 1024, "seed": 7}
            ))

            out = {
                "rx_sin_params_circuit": c_no,
                "rx_con_params_circuit": c_yes,
                "run_sin_params": run_no,
                "run_con_params": run_yes,
                "conclusion": (
                    "add_gate_tool con gate_name='rx' y sin params NO lanza error. "
                    "El circuito resultante lleva rx con param por defecto 0.5 (ver el dict), "
                    "y la distribucion de medicion difiere de la de rx(1.0). "
                    "Fallo silencioso: el agente cree que funciono."
                ),
            }
            dump_json("silent_rx_demo.json", out)
            print(out["conclusion"])


asyncio.run(main())
