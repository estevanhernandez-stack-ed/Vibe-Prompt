#!/usr/bin/env bash
# Verify no vendor API key pattern appears in any committed plugin file.
# This catches accidental key leakage during development.
set -euo pipefail
PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

PATTERNS=(
    "AIza[0-9A-Za-z_-]{35}"
    "sk-ant-(api|admin)[0-9A-Za-z_-]+"
    "sk-[a-zA-Z0-9]{48}"
    "sk-proj-[a-zA-Z0-9_-]+"
)

FAIL=0
for pattern in "${PATTERNS[@]}"; do
    if grep -rE "$pattern" "$PLUGIN_ROOT" --exclude-dir=tests >/dev/null 2>&1; then
        echo "FAIL: key pattern matching $pattern found in plugin files"
        grep -rE "$pattern" "$PLUGIN_ROOT" --exclude-dir=tests | head -5
        FAIL=$((FAIL+1))
    fi
done
echo ""
if [ "$FAIL" -eq 0 ]; then
    echo "PASS: no key patterns detected in plugin files"
fi
[ "$FAIL" -eq 0 ]
