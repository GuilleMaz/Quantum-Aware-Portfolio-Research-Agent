"""Handshake `initialize` + `tools/list` crudos por stdio (sin SDK).

Uso:
    uv run python labs/phase1-mcp-basics/handshake.py financial
    uv run python labs/phase1-mcp-basics/handshake.py qiskit
"""

import json
import os
import subprocess
import sys

CMDS = {
    "financial": ["uvx", "--from", "financial-mcp-server", "--with", "mcp<2", "financial-mcp"],
    "qiskit": ["uvx", "--from", "mcp-qiskit[mcp]", "mcp-qiskit"],
}


def read_until(proc, target_id):
    for raw in proc.stdout:
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            # stdout deberia ser solo JSON-RPC; si aparece texto, lo anotamos
            print("LINEA_NO_JSON:", line)
            continue
        if obj.get("id") == target_id:
            return obj
    return None


def main(server):
    cmd = CMDS[server]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env={**os.environ},
    )
    try:
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "phase1-handshake", "version": "0.1"},
            },
        }
        proc.stdin.write(json.dumps(init_req) + "\n")
        proc.stdin.flush()
        init_resp = read_until(proc, 1)
        print("=== initialize ===")
        print(json.dumps(init_resp, indent=2, ensure_ascii=False))

        # notificacion (sin id): el servidor no responde
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()

        tools_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        proc.stdin.write(json.dumps(tools_req) + "\n")
        proc.stdin.flush()
        tools_resp = read_until(proc, 2)
        print("=== tools/list (resumen) ===")
        if tools_resp and "result" in tools_resp:
            tools = tools_resp["result"].get("tools", [])
            print("count:", len(tools))
            for t in tools:
                print(" -", t.get("name"))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in CMDS:
        print("uso: handshake.py {financial|qiskit}")
        sys.exit(2)
    main(sys.argv[1])
