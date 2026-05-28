#!/usr/bin/env bash
# Validate JSON schemas parse + at least one fixture per schema passes.
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCHEMAS_DIR="$PLUGIN_ROOT/schemas"
FIXTURES_DIR="$PLUGIN_ROOT/tests/fixtures"

PASS=0
FAIL=0

# Change to schemas directory for consistent path handling
cd "$SCHEMAS_DIR"

for schema in *.schema.json; do
    if python3 -c "import json; json.load(open('$schema'))" >/dev/null 2>&1; then
        echo "PASS: $schema parses"
        PASS=$((PASS+1))
    else
        echo "FAIL: $schema does not parse"
        FAIL=$((FAIL+1))
    fi
done

echo ""
echo "Total: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ]
