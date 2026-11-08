"""No model needed: do exactly what the injected ticket asks, against both servers.

This shows the blast radius each server design allows, whatever the model decides.

    uv run demo_b/probe.py
"""

import asyncio
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent
ATTACK_SQL = "SELECT service, token FROM integration_tokens"


async def probe(server: str) -> None:
    print(f"\n######## {server} ########")
    params = StdioServerParameters(command=sys.executable, args=[str(HERE / server)])
    with open(os.devnull, "w") as quiet:  # hide server log lines
        async with stdio_client(params, errlog=quiet) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = {t.name: t for t in (await session.list_tools()).tools}
                for t in tools.values():
                    hints = t.annotations.model_dump(exclude_none=True) if t.annotations else "none"
                    print(f"tool {t.name}: annotations {hints}")
                if "execute_sql" in tools:
                    result = await session.call_tool("execute_sql", {"query": ATTACK_SQL})
                    print(f"\nexecute_sql({ATTACK_SQL!r}) ->\n{result.content[0].text}")
                else:
                    print("\nNo tool can run SQL or touch integration_tokens. The injection has nothing to call.")


async def main() -> None:
    await probe("support_server_vulnerable.py")
    await probe("support_server_fixed.py")


asyncio.run(main())
