#!/usr/bin/env sh
# Demo LLM master-switch remote control (local-only tool, gitignored).
#
# Usage:
#   scripts/demo-llm.sh on [minutes]   # enable the demo LLM (default TTL 60 min)
#   scripts/demo-llm.sh off            # disable it now
#   scripts/demo-llm.sh status         # is it on, and until when?
#   scripts/demo-llm.sh stats          # LLM usage aggregates (public endpoint)
#
# Reads ADMIN_TOKEN and DEMO_API_URL from the repo-root .env (gitignored).

set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"

get_var() {
  grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2-
}

URL="$(get_var DEMO_API_URL)"
TOKEN="$(get_var ADMIN_TOKEN)"

[ -n "$URL" ] || { echo "DEMO_API_URL missing in .env"; exit 1; }

case "${1:-}" in
  on)
    [ -n "$TOKEN" ] || { echo "ADMIN_TOKEN missing in .env"; exit 1; }
    MINUTES="${2:-60}"
    curl -s -X POST "$URL/api/admin/llm" \
      -H "X-Admin-Token: $TOKEN" -H "Content-Type: application/json" \
      -d "{\"enabled\": true, \"ttl_minutes\": $MINUTES}"
    echo ""
    ;;
  off)
    [ -n "$TOKEN" ] || { echo "ADMIN_TOKEN missing in .env"; exit 1; }
    curl -s -X POST "$URL/api/admin/llm" \
      -H "X-Admin-Token: $TOKEN" -H "Content-Type: application/json" \
      -d '{"enabled": false}'
    echo ""
    ;;
  status)
    [ -n "$TOKEN" ] || { echo "ADMIN_TOKEN missing in .env"; exit 1; }
    curl -s "$URL/api/admin/llm" -H "X-Admin-Token: $TOKEN"
    echo ""
    ;;
  stats)
    curl -s "$URL/api/stats"
    echo ""
    ;;
  *)
    echo "usage: $0 on [minutes] | off | status | stats"
    exit 1
    ;;
esac
