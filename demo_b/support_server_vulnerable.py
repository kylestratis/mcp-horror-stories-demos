"""Support-desk server, the Supabase-July-2025 way.

execute_sql runs any SQL with full rights, like an agent holding the
service_role key: it can read integration_tokens and write anywhere.
Messages posted to a ticket are visible to the customer who filed it.
"""

import sqlite3
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DB = Path(__file__).resolve().parent.parent / "runtime" / "support.db"
THREAD_LOG = DB.parent / "ticket_thread.log"  # what the customer sees

mcp = FastMCP("support")


@mcp.tool()
def execute_sql(query: str) -> str:
    """Run a SQL query against the support database and return the rows."""
    db = sqlite3.connect(DB)
    rows = db.execute(query).fetchall()
    db.commit()
    return "\n".join(map(str, rows)) or "OK"


@mcp.tool()
def reply_to_ticket(ticket_id: int, body: str) -> str:
    """Post a message on a support ticket. The customer can see it."""
    db = sqlite3.connect(DB)
    db.execute("INSERT INTO ticket_messages (ticket_id, author, body) VALUES (?, 'agent', ?)", (ticket_id, body))
    db.commit()
    with THREAD_LOG.open("a") as f:
        f.write(f"--- ticket #{ticket_id}, visible to customer\n{body}\n")
    return f"Posted to ticket {ticket_id}."


if __name__ == "__main__":
    mcp.run()
