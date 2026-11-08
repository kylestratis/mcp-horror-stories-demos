"""Launch the fact server twice and print what the client is told each time.

Uses a throwaway counter file, so it does not disturb the live demo's state.

    uv run demo_a/show_rug_pull.py
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from list_tools import fetch_tools, print_tools  # noqa: E402

SERVER = str(Path(__file__).resolve().parent / "fact_server.py")


async def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "FACT_STATE_FILE": f"{tmp}/launches"}
        env.pop("FACT_MODE", None)
        for launch in (1, 2):
            print(f"\n######## Launch {launch}: what the model sees ########")
            print_tools(await fetch_tools(SERVER, env))
            if launch == 1:
                input("\n[You approve this server. Press Enter to restart it...]")


asyncio.run(main())
