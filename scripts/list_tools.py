"""Connect to an MCP server over stdio and print its tools exactly as a client sees them.

    uv run scripts/list_tools.py demo_b/support_server_fixed.py
"""

import asyncio
import hashlib
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def fetch_tools(server_path: str, env: dict[str, str] | None = None):
    params = StdioServerParameters(command=sys.executable, args=[server_path], env=env)
    with open(os.devnull, "w") as quiet:  # hide server log lines
        async with stdio_client(params, errlog=quiet) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return (await session.list_tools()).tools


def print_tools(tools) -> None:
    for t in tools:
        digest = hashlib.sha256((t.description or "").encode()).hexdigest()[:12]
        print(f"\n== {t.name}  (description sha256 {digest})")
        if t.annotations:
            print(f"   annotations: {t.annotations.model_dump(exclude_none=True)}")
        print("   " + (t.description or "").replace("\n", "\n   "))


if __name__ == "__main__":
    print_tools(asyncio.run(fetch_tools(sys.argv[1])))
