# Rollback workflow — remediate

When an auto-write diff lands wrong (broke a test, drifted the voice, applied a
contradiction that wasn't actually a contradiction), the user runs:

```
/vibe-prompt:remediate --rollback <ISO-timestamp>
```

This restores all files modified in that backup batch to their pre-application
state. Atomic — all or none. If any restore fails, the partial restore is rolled
back and an error surfaces.

## Locate the backup batch

The `<ISO-timestamp>` argument matches the directory name under
`.vibe-prompt/remediate/backup/`. Format: `YYYY-MM-DD-HHMM` (minute precision,
same as the `runId` that created it).

Algorithm:
1. List `.vibe-prompt/remediate/backup/*/` directories.
2. Find the entry whose name matches the timestamp argument exactly.
3. If not found, fuzzy-match against the most-recent N batches (e.g., `2026-05-30`
   matches `2026-05-30-0900` if it's the only batch on that date).
4. If still ambiguous or absent, error out (see §Missing-backup error below).

## Restore each .bak

Walk the batch directory. For each `.bak` file:
1. Compute the source path by stripping `.bak` from the filename and mapping
   the batch-relative path to the source-tree-relative path.

   Example: `.vibe-prompt/remediate/backup/2026-05-30-0900/src/lib/gemini.ts.bak`
   → restore target `src/lib/gemini.ts`.

2. Read the `.bak` content.
3. Verify the current source file exists at the target path. If not, mark as
   "target-missing" and add to the partial-failure list.
4. Read the current source file's SHA-256 hash. Compare against the `appliedHash`
   recorded in `runs.jsonl` for this batch's apply entries.
   - If hash matches → the file is unchanged since apply; safe to restore.
   - If hash differs → the user has edited the file since apply. Add to the
     `drift-detected` list — user decides whether to proceed.

## Atomic semantics — all-or-none

The restore is atomic. Either all files in the batch successfully restore, or none
do. Implementation:

1. **Stage phase** — copy each `.bak` to a temp file in the same directory as the
   target (`<target>.rollback-staged`). Do not overwrite the target yet.
2. **Verify phase** — if any stage step failed (disk full, permissions, etc.),
   delete all `.rollback-staged` files and abort.
3. **Commit phase** — rename each `.rollback-staged` to `<target>` atomically (the
   OS-level rename is atomic on POSIX; Windows uses `MoveFileEx` with replace).

If a drift-detected file is in the batch, prompt the user via AskUserQuestion:
> File `<path>` has changed since apply. Restoring will overwrite your edits.
> Continue? (y/n/skip-this-file)

`skip-this-file` proceeds with the rest of the batch but leaves the drifted file
alone. Logs to `runs.jsonl` with `action: rolled-back` and a `skippedFiles` array.

## Log to runs.jsonl

After successful rollback, append one entry to `.vibe-prompt/remediate/state/runs.jsonl`:

```json
{
  "timestamp": "2026-05-30T11:00:00Z",
  "runId": "remediate-2026-05-30-1100",
  "action": "rolled-back",
  "rolledBackBatchPath": ".vibe-prompt/remediate/backup/2026-05-30-0900/",
  "filesRestored": ["src/lib/gemini.ts", "src/lib/ConfigService.ts"],
  "skippedFiles": [],
  "driftDetected": []
}
```

Then friction-log `auto-write-rolled-back` (high confidence) — the friction trigger
that signals the rubric or category routing may need tuning. The friction entry
references the original apply's runId so `:evolve-prompt` can correlate.

## Missing-backup error

If the user passes a timestamp that doesn't match any batch:

```
Backup batch not found: <timestamp>

Available batches:
  2026-05-30-0900  (2 files: src/lib/gemini.ts, src/lib/ConfigService.ts)
  2026-05-28-1430  (1 file: src/lib/gemini.ts)

Re-run with one of the timestamps above, or omit the argument to roll back the
most recent batch.
```

`:remediate --rollback` (no argument) defaults to the most recent batch — fast path
for "undo the last apply."

## Partial backup — recovery

A partial backup occurs when a previous apply was interrupted (process killed
mid-batch) and only some `.bak` files exist. The apply itself succeeded for the
files it touched, but the batch is structurally incomplete.

Detection: cross-reference the batch directory's `.bak` files against the
`runs.jsonl` `applied` entries that point at this batch path. If the apply count
exceeds the `.bak` count, the batch is partial.

Recovery: surface the partial state to the user:

> Batch `2026-05-30-0900` is partial: 2 apply entries in runs.jsonl, 1 .bak file
> in backup dir. Restoring the partial batch will leave at least one file in its
> post-apply state. Continue? (y/n)

If the user proceeds, restore what's available, log the partial restore to
`runs.jsonl`, and friction-log `partial-rollback-encountered` (medium).

## Backup retention

`remediate.backupRetentionDays` in `config.json` defaults to 30. v0.5 does NOT
auto-prune — retention is policy-only. A future maintenance command may prune
batches older than the retention window. Until then, backup batches accumulate;
the user is responsible for `rm -rf .vibe-prompt/remediate/backup/<old>/` when
the dir grows.

## Never

- Rollback a batch from a different `runId` than the current run (would mix
  semantics).
- Modify the source tree without verifying all stage-phase copies succeeded.
- Delete a `.bak` file after rollback — keep it as a second-chance undo
  (the rollback itself becomes the new "applied" state that subsequent rollbacks
  can undo).
- Skip the friction-log entry — `auto-write-rolled-back` is the strongest signal
  the confidence rubric is mis-calibrated, and `:evolve-prompt` needs to see it.
