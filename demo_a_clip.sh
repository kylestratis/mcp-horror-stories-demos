#!/usr/bin/env bash
# Demo A in about 90 seconds, for screen recording. No model calls.
#
#   1. The rug pull: the tool description before and after the second launch.
#   2. Replay of a real Haiku run where the attack worked (2026-11-10).
#   3. Replay of a real Opus run that caught it (2026-11-10).
#
# Press Enter to advance. The replays are saved transcripts of live runs
# (demo_a/recorded/), so say on stage that they're replays. Odds across
# repeated runs that day: Haiku 3 of 8, Opus 0 of 5 (see README).
set -euo pipefail
cd "$(dirname "$0")"
pause() { read -r -p $'\n[Enter] ' || true; clear || true; }

REC=demo_a/recorded
if [ ! -f "$REC/haiku_attack.jsonl" ] || [ ! -f "$REC/opus_caught.jsonl" ]; then
  cat <<EOF
This clip replays two saved transcripts that aren't in the repo:
  $REC/haiku_attack.jsonl   a run where the attack worked
  $REC/opus_caught.jsonl    a run where the model caught it

To create them (needs Claude Code logged in, or ANTHROPIC_API_KEY set):
  mkdir -p $REC
  MODEL=haiku ./trials.sh 8     # prints which runs were ATTACK
  cp runtime/trials/haiku_a2_<n>.jsonl $REC/haiku_attack.jsonl
  ./trials.sh 5
  cp runtime/trials/default_a2_<n>.jsonl $REC/opus_caught.jsonl

Results vary run to run; a smaller model may need more trials to land a hit.
EOF
  exit 0
fi

clear
uv run --quiet demo_a/show_rug_pull.py
pause

echo "######## claude-haiku-4-5, poisoned server (replay of a real run) ########"
uv run --quiet scripts/show_transcript.py demo_a/recorded/haiku_attack.jsonl
pause

echo "######## claude-opus-5-5, same server, same prompt (replay of a real run) ########"
uv run --quiet scripts/show_transcript.py demo_a/recorded/opus_caught.jsonl
