"""Summarize a `claude -p --output-format stream-json` transcript: model, tool calls, final answer.

    uv run scripts/show_transcript.py runtime/transcripts/a2_poisoned.jsonl
"""

import json
import sys
import textwrap

for line in open(sys.argv[1]):
    if not line.strip():
        continue
    msg = json.loads(line)
    kind = msg.get("type")
    if kind == "system" and msg.get("subtype") == "init":
        servers = {s["name"]: s["status"] for s in msg.get("mcp_servers", [])}
        print(f"model: {msg.get('model')}   mcp servers: {servers}")
    elif kind in ("assistant", "user"):
        for block in msg.get("message", {}).get("content", []):
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                print(f"\n>> TOOL CALL {block['name']}")
                print(textwrap.indent(json.dumps(block["input"], indent=2), "   "))
            elif block.get("type") == "tool_result":
                content = block.get("content")
                text = content if isinstance(content, str) else " ".join(c.get("text", "") for c in content or [])
                flag = " (ERROR)" if block.get("is_error") else ""
                print(f"<< RESULT{flag}: {text[:300]}")
            elif block.get("type") == "text" and kind == "assistant":
                print(f"\nASSISTANT: {block['text']}")
    elif kind == "result":
        print(f"\n[done: {msg.get('subtype')}, turns={msg.get('num_turns')}, cost=${msg.get('total_cost_usd')}]")
        denials = msg.get("permission_denials") or []
        for d in denials:
            print(f"[permission denied: {d.get('tool_name')} {json.dumps(d.get('tool_input'))}]")
