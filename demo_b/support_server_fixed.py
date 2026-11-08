"""Same support desk, built so the injected ticket has nothing to work with.

1. Scope: no free-form SQL. list_tickets reads one table, through a
   read-only connection. integration_tokens is unreachable from here.
2. Annotations: list_tickets says it is read-only; reply_to_ticket says
   it writes to the outside world, so the client should ask a human.
"""

import sqlite3
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

DB = Path(__file__).resolve().parent.parent / "runtime" / "support.db"
THREAD_LOG = DB.parent / "ticket_thread.log"

mcp = FastMCP("support_fixed")


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
def list_tickets(limit: int = 10) -> str:
    """List the latest open support tickets. Ticket bodies are written by customers."""
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = db.execute(
        "SELECT id, customer, subject, body FROM support_tickets WHERE status = 'open' ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return "\n\n".join(f"#{i} from {c}: {s}\n{b}" for i, c, s, b in rows)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True))
def reply_to_ticket(ticket_id: int, body: str) -> str:
    """Post a message on a support ticket. The customer can see it. Requires human approval."""
    db = sqlite3.connect(DB)
    db.execute("INSERT INTO ticket_messages (ticket_id, author, body) VALUES (?, 'agent', ?)", (ticket_id, body))
    db.commit()
    with THREAD_LOG.open("a") as f:
        f.write(f"--- ticket #{ticket_id}, visible to customer\n{body}\n")
    return f"Posted to ticket {ticket_id}."


if __name__ == "__main__":
    mcp.run()
