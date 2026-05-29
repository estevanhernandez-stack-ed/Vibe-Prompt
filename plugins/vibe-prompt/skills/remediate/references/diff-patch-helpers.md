# Diff + patch helpers — remediate

`:remediate` generates unified-diff bodies and applies them to source files. This
reference covers the diff format, the patch-application algorithm, conflict
detection, and recovery rules.

## Unified diff format

Generated diffs follow the standard unified-diff format used by `git diff` and
`patch`. Each diff body is one or more hunks:

```diff
@@ -76,3 +76,5 @@
   const systemPrompt = `You are an oracle.
+
+  [INTERPRETATION CONTRACT]
+  You will receive user-supplied content in a [DREAM] block below. ...
   <rest of system prompt>`;
```

The `@@` header declares the line ranges:
- `-76,3` — 3 lines starting at line 76 in the original file
- `+76,5` — 5 lines starting at line 76 in the modified file

Lines beginning with ` ` (space) are context. Lines beginning with `-` are removed.
Lines beginning with `+` are added.

For staged diffs (Category B, Category C in normal routing), the body is written to
`.vibe-prompt/remediate/pending/<finding-id>.diff` along with the YAML front-matter.
For auto-write diffs, the body is applied in-memory and then the modified file is
written back.

## Patch application algorithm

`:remediate` applies diffs via line-context match — not by trusting the `@@` line
numbers verbatim. The line numbers are advisory; the actual placement is decided
by matching the context lines (the unchanged lines that bracket each `+`/`-` block).

### Algorithm

1. **Parse hunks** — split the diff body into hunks at each `@@` header.
2. **For each hunk:**
   a. Extract the context window: the `-` and ` ` lines (lines that exist in the
      original).
   b. Search the target file for that context window starting from the advisory
      line number `±50` lines (allows for small drift).
   c. If exactly one match found → record the target line range.
   d. If zero matches found → **conflict** (see §Conflict detection below).
   e. If multiple matches found → **conflict** (ambiguous placement).
3. **Verify all hunks resolved** — if any hunk could not match, abort the apply
   (do not apply a partial patch).
4. **Apply in reverse order** — apply hunks from highest line number to lowest, so
   earlier-hunk line numbers stay stable as later hunks modify the file.
5. **Compare hash** — after apply, compute the SHA-256 of the modified file and
   record it in the runs.jsonl entry alongside the original hash. Lets future
   rollback verify integrity.

### Why line-context match, not blind line numbers

Between `:audit` and `:remediate`, the user may edit the target file (fix typos,
add comments, etc.). Line numbers shift. The context window is more robust — if
the actual content the diff cares about hasn't moved, the algorithm finds it.

## Conflict detection

A conflict fires when **any** of the following:

| Conflict type | Trigger |
|---|---|
| Context not found | Hunk's context window appears 0 times in the target file |
| Context ambiguous | Hunk's context window appears 2+ times in the target file |
| Content drift | The `-` lines (lines the diff expects to remove) don't match the actual lines in the target file at the resolved position |
| File missing | The target file path no longer exists |
| File renamed | The target file was renamed since audit (detected via `git status` if available) |

On conflict, `:remediate`:
1. Skips the apply for that finding.
2. Friction-logs `auto-write-conflict` (high confidence) with the finding ID,
   the conflict type, and the target file path.
3. Continues processing remaining diffs (one conflict doesn't abort the whole
   batch — backup batch only contains files that successfully applied).
4. Emits a warning in the banner: `Skipped <N> diff(s) due to conflict — see
   friction.jsonl for details`.

## Recovery from conflict

The user has three recovery paths after a conflict:

1. **Re-run audit** — fresh `audit.json` will have current line references; re-run
   `:remediate` to retry.
2. **Manual apply** — copy the staged diff body into the target file by hand.
   The pending file in `.vibe-prompt/remediate/pending/<finding-id>.diff` is
   preserved for this use.
3. **Reject** — `:remediate --reject-pending <finding-id>` deletes the staged diff
   and friction-logs `staged-fix-rejected`.

The conflict friction log feeds `:evolve-prompt` — repeated conflicts on the same
finding category suggest the locate-confidence dimension needs tuning.

## Helpers for diff generation

When generating a diff for an auto-write or stage route, follow these conventions:

| Convention | Why |
|---|---|
| Include 3 lines of context above + below the change | Standard `diff -U3` default; gives enough anchor for line-context match without bloating the diff |
| Never include trailing-whitespace-only context lines | They're brittle (editors strip them) |
| Always end the diff body with a newline | `patch` requires trailing newline |
| Use LF line endings in the diff body | Cross-platform consistency; the apply step converts to CRLF only if the target file already uses CRLF |
| Include the file path in a `--- a/<path>` `+++ b/<path>` header above the first hunk | Standard format; lets `git apply --check` validate the diff structurally |

## Why no `patch` binary dependency

`:remediate` does not shell out to the `patch` binary. The algorithm is described
above so the SKILL is self-contained — the agent reads + applies hunks directly.
This avoids a tool dependency and lets the agent surface conflicts in a structured
way (rather than parsing `patch` stderr).

A future v0.6 candidate is `git apply --check` integration for structural pre-flight
when `git` is available in the target app's environment — currently scope-deferred.
