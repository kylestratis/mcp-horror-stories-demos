#!/usr/bin/env bash
# Put every demo back to its starting state. Run between takes.
set -euo pipefail
cd "$(dirname "$0")"

rm -f runtime/outbox.log runtime/fact_launches runtime/ticket_thread.log
uv run --quiet demo_b/seed_db.py
echo "Reset: outbox empty, fact server will be benign on its next launch, support.db reseeded."
