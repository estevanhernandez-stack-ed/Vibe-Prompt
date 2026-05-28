#!/usr/bin/env bash
# Verify every reference link in every SKILL.md points to an existing file.
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$PLUGIN_ROOT/skills"

PASS=0
FAIL=0

# Find all SKILL.md files
while IFS= read -r skill_md; do
    skill_dir="$(dirname "$skill_md")"
    # Extract references/*.md links
    while IFS= read -r ref; do
        ref_path="$skill_dir/$ref"
        if [ -f "$ref_path" ]; then
            PASS=$((PASS+1))
        else
            echo "FAIL: $skill_md references $ref (resolved $ref_path) — missing"
            FAIL=$((FAIL+1))
        fi
    done < <(grep -oE 'references/[A-Za-z0-9_-]+\.md' "$skill_md" || true)
done < <(find "$SKILLS_DIR" -name SKILL.md)

echo ""
echo "Total: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ]
