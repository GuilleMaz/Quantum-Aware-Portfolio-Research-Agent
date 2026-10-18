"""Llama a herramientas del servidor financiero y guarda la salida real.

Ejemplos:
    uv run python labs/phase1-mcp-basics/call_tool.py get_price AAPL
    uv run python labs/phase1-mcp-basics/call_tool.py get_fundamentals AAPL
    uv run python labs/phase1-mcp-basics/call_tool.py get_momentum AAPL
"""

import asyncio
import json
import sys

from common import dump_json, financial_params


def unwrap(result):
    """Devuelve un dict con content/structured_content/is_error y el payload parseado."""
    out = {
        "is_error": bool(getattr(result, "is_error", False)),
        "content": [],
        "structured_content": getattr(result, "structured_content", None),
    }
    for block in getattr(result, "content", []) or []:
        if hasattr(block, "text"):
            out["content"].append({"type": "text", "text": block.text})
        else:
            out["content"].append(str(block))
    # Intento de parsear el doble encoding {"result": "<json string>"}
    sc = out["structured_content"]
    parsed = None
    if isinstance(sc, dict) and "result" in sc:
        inner = sc["result"]
        if isinstance(inner, str):
            try:
                parsed = json.loads(inner)
            except Exception:
                parsed = inner
        else:
            parsed = inner
    out["parsed"] = parsed
    return out


async def main(tool: str, symbol: str):
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client

    async with stdio_client(financial_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, {"symbol": symbol})
            data = unwrap(result)
            data["tool"] = tool
            data["arguments"] = {"symbol": symbol}
            dump_json(f"{tool}_{symbol}.json", data)
            print(json.dumps(data, indent=2, ensure_ascii=False, default=str)[:2000])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("uso: call_tool.py <tool> <SYMBOL>")
        sys.exit(2)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
