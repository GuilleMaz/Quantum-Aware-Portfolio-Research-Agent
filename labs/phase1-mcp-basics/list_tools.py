"""Lista las herramientas de un servidor MCP y las guarda en snapshots/.

Uso:
    uv run python labs/phase1-mcp-basics/list_tools.py financial
    uv run python labs/phase1-mcp-basics/list_tools.py qiskit
"""

import asyncio
import json
import sys

from common import dump_json, financial_params, qiskit_params, tool_to_dict


async def main(server: str):
    params = financial_params() if server == "financial" else qiskit_params()
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            tools = await session.list_tools()
            data = {
                "server": server,
                "protocol_version": getattr(init, "protocol_version", None),
                "capabilities": init.capabilities.model_dump(mode="json") if hasattr(init.capabilities, "model_dump") else str(init.capabilities),
                "server_info": init.server_info.model_dump(mode="json") if hasattr(init.server_info, "model_dump") else str(init.server_info),
                "count": len(tools.tools),
                "tools": [tool_to_dict(t) for t in tools.tools],
            }
            dump_json(f"{server}_tools.json", data)
            print(f"{server}: {len(tools.tools)} tools")
            for t in tools.tools:
                print(" -", t.name)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("financial", "qiskit"):
        print("uso: list_tools.py {financial|qiskit}")
        sys.exit(2)
    asyncio.run(main(sys.argv[1]))
