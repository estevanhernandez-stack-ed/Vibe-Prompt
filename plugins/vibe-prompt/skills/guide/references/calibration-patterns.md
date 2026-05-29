# LLM-judge calibration patterns — vibe-prompt v0.3

All four patterns apply together (not negotiable bundle) in both `:audit`'s clarity-scoring meta-prompt and `:eval`'s drift-detection + behavioral-scoring judge.

## 1. SWRS structure (Strengths/Weaknesses/Reasoning/Score)

Judge returns JSON with this exact shape:

```json
{
  "strengths": ["array of 1-3 specific strengths"],
  "weaknesses": ["array of 1-3 specific weaknesses"],
  "reasoning": "prose explaining the assessment in 2-4 sentences",
  "score": 1-10
}
```

Strengths and weaknesses come BEFORE reasoning. Reasoning comes BEFORE score. The order matters — when the model emits reasoning tokens before committing to a verdict, it substantially reduces the tendency to default to middling scores (Anthropic training notes; verified pattern).

## 2. Long CoT before verdict

Judge prompt explicitly requests step-by-step reasoning before the score. This reduces self-preference bias (Chen et al. 2025-era research). For each criterion in the rubric, the judge must articulate the analysis BEFORE outputting any score.

Example judge prompt fragment:

> "Before scoring, walk through your analysis step by step. For each dimension (schema tightness, persona consistency, instruction clarity, token efficiency), reason through what you observe in the output. Cite specific phrases. THEN provide your scores."

## 3. Swap-and-Discard (position bias mitigation)

For comparative judgments (eval's drift detection: prod output vs baseline output), run the judge TWICE:

- Run 1: Output A = prod, Output B = baseline
- Run 2: Output A = baseline, Output B = prod (swapped)

If the judge favors "Output A" in BOTH runs (i.e., the favored position is the same regardless of content), DISCARD the comparison as a position-bias tie. Log the tie. Do not let it contribute to the drift findings.

If the judge favors the SAME UNDERLYING CONTENT in both runs (favors A in run 1 and B in run 2 — both pointing at the same actual output), accept the finding.

Cost: doubles judge calls per eval pair. Default: enabled. User can opt out with `:eval --no-swap` for cost-sensitive runs.

## 4. Verbosity penalty in rubric

Judge prompt explicitly instructs:

> "Penalize unnecessary elaboration. Quality is not length. An output that says the same thing in fewer words scores higher on token efficiency. Padded outputs that game evaluators should score lower."

This prevents verbosity-bias — the tendency for judges to prefer longer outputs even when shorter ones are better.

## 5. Lineage-overlap warning (carried forward from v0.2)

Every LLM-judge finding ships with the cross-vendor evaluator-drift footer (vibe-prompt v0.2 pattern). The footer names the evaluator identity so the user calibrates accordingly. v0.3 keeps this pattern — see `vibe-prompt:eval` SKILL for the footer template.
