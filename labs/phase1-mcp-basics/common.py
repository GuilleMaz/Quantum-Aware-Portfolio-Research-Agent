"""Helpers compartidos para los experimentos de la Fase 1."""

import json
import os
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

LAB_DIR = Path(__file__).resolve().parent
SNAPSHOTS = LAB_DIR / "snapshots"
SNAPSHOTS.mkdir(exist_ok=True)


def financial_params():
    args = ["--from", "financial-mcp-server", "--with", "mcp<2", "financial-mcp"]
    env = {**os.environ}
    return StdioServerParameters(command="uvx", args=args, env=env, read_timeout_seconds=60.0)


def qiskit_params():
    args = ["--from", "mcp-qiskit[mcp]", "mcp-qiskit"]
    env = {**os.environ}
    return StdioServerParameters(command="uvx", args=args, env=env, read_timeout_seconds=120.0)


async def open_session(params):
    """Context manager helper: devuelve (read, write) via stdio_client."""
    return stdio_client(params)


def dump_json(name, data):
    path = SNAPSHOTS / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"saved {path}")
    return path


def tool_to_dict(tool):
    try:
        return tool.model_dump(mode="json")
    except Exception:
        return json.loads(tool.model_dump_json())
