import asyncio, json, os
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def main():
    params = StdioServerParameters(
        command="uvx",
        args=["--from", "financial-mcp-server", "--with", "mcp<2", "financial-mcp"],
        env=None,
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print("INIT:", init)
            tools = await session.list_tools()
            print("NUM TOOLS:", len(tools.tools))
            for t in tools.tools:
                print(t.name)

asyncio.run(main())
