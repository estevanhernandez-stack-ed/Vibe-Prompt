# Swap-and-Discard — eval

Position-bias mitigation for the LLM-judge layer's comparative judgments.

## When it applies

For every (prompt × model) pair where the judge compares prod output vs baseline output to detect drift.

## Workflow

1. **Run 1 (original order):** dispatch judge subagent with Output A = prod, Output B = baseline. Capture judgment.

2. **Run 2 (swapped order):** dispatch judge subagent with Output A = baseline (swapped to position 1), Output B = prod (swapped to position 2). Capture judgment.

3. **Compare:**
   - **Content-consistent (accept):** judge favors the SAME UNDERLYING OUTPUT in both runs. Example: judge says "Output A is better" in run 1 (pointing at prod), and "Output B is better" in run 2 (still pointing at prod). The judge is responding to the content, not the position. **Accept** the finding.
   - **Position-tied (discard):** judge favors the SAME POSITION in both runs. Example: judge says "Output A is better" in both runs (pointing at prod in run 1, baseline in run 2). The judge is responding to the position, not the content. **Discard** the finding as position-bias artifact.

4. **Log:** in `run-result.json`, the `llmJudge.swapAndDiscard` block records `enabled: true`, `tiedAndDiscarded: <bool>`, and a summary of both judgments.

## Cost note

Swap-and-Discard doubles LLM-judge calls per eval (prod-vs-baseline) pair. For a 14-prompt sweep with one fixture each, this means 28 judge calls instead of 14. Cost gate (default $2.00 ceiling) absorbs this for typical Gemini-tier rates (~$0.02 per judge call on Claude in-session = $0 against ceiling, since in-session calls bill against the user's session not the plugin's vendor budget).

User can disable via `:eval --no-swap` for cost-sensitive runs.

## Friction trigger

If more than 30% of judge calls in a single `:eval` run are discarded as position ties, friction-log `swap-and-discard-tie-rate-over-30pct` with medium confidence. Signal: the judge prompt may need tightening OR a different model should be used as judge.
