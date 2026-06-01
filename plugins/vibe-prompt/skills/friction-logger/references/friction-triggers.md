# Friction triggers — vibe-prompt

Single source of truth for which command logs which friction at which confidence. Agents do NOT tune per call.

## scan triggers

| Trigger code | Confidence | When |
|---|---|---|
| `no-recognized-stack` | high | No `package.json` AND no `pyproject.toml`/`requirements.txt` |
| `registry-detected-but-empty-entries` | high | Registry found, but extraction yielded zero entries |
| `model-identifier-unrecognized` | high | Model string matches no published-model regex (per F6 list) |
| `low-confidence-detections-over-40pct` | medium | More than 40% of inline detections are low-confidence (per persona-extraction.md §confidence) |
| `inline-prompt-without-fallback-aggregate` | low | At least 3 inline sites with no fallback (logged once per scan) |

## audit triggers

| Trigger code | Confidence | When |
|---|---|---|
| `f6-suspect-model-detected` | high | F6 fires with the suspect-model variant |
| `f2-contradiction-cross-file-attempted` | medium | F2 detection surfaced a likely contradiction but the 1-hop trace couldn't fully resolve it |
| `rubric-default-recommendation-felt-generic` | medium | Agent's self-read of the just-rendered recommendation says it lacks app-specific detail |
| `inventory-schema-violation` | high | inventory.json failed schema validation on read |
| `f9-fired-but-prompt-already-has-date-grounding` | low | User reports the prompt already has date context via a path the detection missed (composer layer or custom injection not recognized by step B); tune the step-B heuristic |
| `injection-resistance-dimension-flat-across-prompts` | medium | All prompts in the inventory score the same on injectionResistance (all exactly 10 or all exactly the same deducted value); dimension formula may not be sensitive enough, OR app has uniform composition — verify manually |
| `f12-api-parameter-detection-low-confidence` | medium | F12 detection fell back to layer-order check because the composer layers had `apiParameter: null` or `apiParameterConfidence < 0.6`; first-run-setup's apiParameter heuristics missed this app's call pattern |
| `f13-fired-but-prompt-intentionally-flexible-output` | low | User reports F13 fired on a prompt where output flexibility is intentional (e.g., creative-discovery, evaluator-judge); add the prompt id to `audit.f13.outputFormatExceptions` config array |
| `f13-recommended-fix-applied-and-eval-confirms-output-stability` | positive | After applying F13's recommended `[OUTPUT FORMAT:]` declaration and re-running `:eval`, output value-type-drift cleared; the F13 detection rule + recommendation template are paying off |

## first-run-setup triggers

| Trigger code | Confidence | When |
|---|---|---|
| `composer-mimic-confirmation-required` | medium | User had to manually correct the captured composer pattern |
| `agent-detection-fallback-to-interview` | medium | Self-id failed all detection signals and had to ask user |
| `inventory-not-found` | high | `.vibe-prompt/state/inventory.json` missing and user couldn't provide a manual one |

## eval triggers

| Trigger code | Confidence | When |
|---|---|---|
| `key-pattern-in-state-file` | high | Pre-run guardrail caught a state file with a key pattern |
| `cost-ceiling-exceeded` | high | Run aborted partway through |
| `vendor-sdk-not-installed` | high | Plugin needed a vendor SDK that isn't bundled (e.g., OpenAI in v0.1) |
| `model-cost-rate-unknown` | medium | Estimated cost using conservative fallback (model not in rate table) |
| `vendor-api-error` | medium | Vendor returned 5xx after retry |
| `vendor-rate-limit-exhausted` | medium | Vendor returned 429 twice |
| `llm-judge-finding-dismissed-as-bias` | low | User flagged a judge finding as bias-only, not real drift |
| `fixture-synthesis-low-confidence` | low | Agent's confidence in a synthesized fixture is low |
| `injection-attack-succeeded` | high | Inject-attack eval ran and at least one model honored at least one attack fixture (model produced content matching the injected directive instead of maintaining its system role); review composition and add defense directives — cross-plugin handoff to `/vibe-sec:audit` recommended |
| `value-type-drift-fired-but-types-are-compatible` | low | User reports the detected value-type-drift is intentional (OUTPUT_SCHEMA is intentionally loose, accepting multiple types); tune the detection to recognize union declarations in OUTPUT_SCHEMA |

## radar triggers

| Trigger code | Confidence | When |
|---|---|---|
| `radar-cache-older-than-7-days` | low | Posture detected stale cache |
| `vendor-news-source-unreachable` | medium | Web fetch failed for a vendor blog/news source |

## router triggers

| Trigger code | Confidence | When |
|---|---|---|
| `audit-older-than-14-days` | low | Posture branch detects stale audit |
| `eval-older-than-30-days` | low | Posture detected stale last eval run |

## evolve-prompt triggers

| Trigger code | Confidence | When |
|---|---|---|
| `no-sessions-in-30-days` | low | Insufficient data to make any proposal |

## grade triggers

| Trigger code | Confidence | When |
|---|---|---|
| `weight-override-suggested-and-rejected` | low | Plugin suggested a dimension weight override; user declined. |
| `regression-flagged` | high | A prompt's composite regressed vs baseline. |
| `regression-flagged-and-accepted-as-baseline` | medium | User accepted a regression as the new baseline via `--accept-regression`. Signal that monotonic discipline may be wrong here, OR scoring has calibration issue. |
| `composite-score-flat-after-fix` | medium | User claims to have fixed a prompt finding but composite didn't move. Signal that dimension formula isn't sensitive enough OR fix didn't land. |
| `swap-and-discard-tie-rate-over-30pct` | medium | More than 30% of judge calls discarded as position-bias ties. Tighten judge prompt or change judge model. |

## iterate triggers

| Trigger code | Confidence | When |
|---|---|---|
| `iterate-suggestion-implemented` | high | User actually built a `:iterate` suggestion (verifiable by next `:scan` finding the new prompt). Positive signal — suggestion engine is valuable. |
| `iterate-suggestion-dismissed-as-off-domain` | medium | User flagged a suggestion as wrong for the app. Signal to tighten domain detection. |

## remediate triggers (v0.5)

| Trigger code | Confidence | When |
|---|---|---|
| `staged-fix-applied-and-eval-confirms-improvement` | high | After `:remediate --apply-pending <findingId>` and a follow-up `:eval` + `:grade`, the prompt's composite advanced (positive signal — the recommendation template is paying off). Validates the diff-category template, the confidence rubric, and the post-apply guidance loop. |
| `staged-fix-rejected` | medium | User reviewed a staged diff and rejected it via `:remediate --reject-pending <findingId>`. Signal that the confidence rubric over-rated the proposal, OR the template for that finding category needs tuning for this app's voice. Tune category routing or rubric weights. |
| `auto-write-rolled-back` | high | User rolled back an auto-applied diff via `:remediate --rollback <ISO-timestamp>`. Strong signal that the auto-write confidence threshold is too low for the affected category, OR the diff template doesn't fit this app's structure. Lower the `autoApplyThreshold` OR tune the category template. |
| `composer-auto-generation-confidence-low` | medium | `:first-run-setup` ran composer.json auto-generation and produced `globalConfidence < 0.5` (or fewer than 2 layers identified). Signal that the composer-detection heuristics missed this app's pattern. Extend the layer-classification regex catalog or surface a manual-verification prompt. |

## remediate triggers (v0.6)

| Trigger code | Confidence | When |
|---|---|---|
| `auto-handoff-vibe-sec-completed` | positive | `:remediate --auto-handoff-vibe-sec` invoked vibe-sec:audit successfully on an F12 critical finding; vibe-sec returned a non-error exit code and the handoff result file landed at `.vibe-prompt/remediate/state/handoff-vibe-sec-<timestamp>.json`. The auto-handoff path paid off (boundary review fired without manual prompting). |
| `auto-handoff-vibe-sec-unavailable` | medium | `:remediate --auto-handoff-vibe-sec` flag was set BUT vibe-sec was not installed (Skill tool absent for `vibe-sec:audit`). `:remediate` fell back to v0.5 banner-only behavior. Surface in the banner so the user can install vibe-sec; don't block the rest of the run. |
| `category-b-voice-frame-detection-confidence-low` | medium | Category B voice-frame detection ran and produced overall confidence < 0.6 (e.g., the global directive's voice rules were vague, OR voice-frame phrase pattern matches were sparse). Diff is staged regardless; signal that `voice-frame-detection.md` heuristics need tuning for this app's voice register. |
| `category-b-voice-frame-rewrite-rejected` | low | User reviewed a staged Category B voice-frame rewrite (`subCategory: "voice-frame-rewrite"`) and rejected it via `:remediate --reject-pending <findingId>`. Signal that the voice-rule extraction misread the global directive OR the rewrite template doesn't match the app's preferred phrasing. Cluster rejections by `voiceFrameRewriteRationale` before proposing a change. |

## v0.7 triggers (generalization completeness)

Nine new triggers covering multi-composer detection, workspace-awareness, Category D migrations, F6 suspect-model, consolidated-diff routing, and F12 severity-decoupling positive signals.

| Trigger code | Confidence | When |
|---|---|---|
| `composer-multiplicity-detected` | positive | `:first-run-setup` classified the app as `kind: "multi-composer"` or `"multi-call-site"` or `"shared-package"` and emitted a `composers[]` array of length ≥2. Positive signal — the v0.7 multi-composer detector successfully recognized a composition topology that v0.6 would have collapsed into a single composer (with attendant false positives/negatives). Validates the kind-classification heuristic for this app's SDK-call shape. |
| `composer-kind-detection-ambiguous` | medium | `:first-run-setup` ran kind classification but the per-composer `globalConfidence` averaged below 0.6 across the emitted `composers[]` array, OR the kind heuristic surfaced two plausible kinds (e.g., `multi-composer` vs `shared-package` both scored within 0.1). Signal that `composer-kinds.md` heuristics need tuning for this app's topology — extend the kind-detection rules or surface a manual-verification prompt. |
| `workspace-detection-confidence-low` | medium | `:scan` workspace detection ran but produced low confidence — e.g., `workspaceKind: "unknown"` despite multiple `package.json` files, OR detected `npm-workspaces` from declaration but the globs didn't expand to any actual workspace directories. Signal that `workspace-detection.md` rules need extension for this app's monorepo shape. |
| `scan-excludes-recommended-but-not-applied` | low | `:scan` auto-detected candidate exclude globs (`vibe-*/`, `*-main/`, `_ARCHIVE_*/`) but the user has not added them to `config.scan.excludes`. Low confidence — surface a one-time banner suggesting the user confirm the recommendation; do not auto-apply (excludes are a load-bearing config decision). |
| `category-d-migration-applied-and-eval-confirms-no-regression` | positive | After `:remediate --apply-inline-to-registry` / `--apply-typed-renderer` / `--apply-model-consolidation` and a follow-up `:eval`, no regression detected on the prompt's composite. Positive signal — the Category D migration template paid off without behavioral cost. Validates the D-1/D-2/D-3 diff template, the routing default, and the migration ratchets. |
| `category-d-migration-rejected` | low | User rejected a staged Category D diff via `:remediate --reject-pending <findingId>` (D-1 inline-to-registry, D-2 typed-renderer, or D-3 model-consolidation). Cluster rejections by `migrationKind` before proposing changes — a D-1-heavy rejection pattern means the registry-id derivation needs tuning; D-2-heavy means the typed-renderer interface shape is wrong for this app; D-3-heavy means the `src/config/ai.ts` convention doesn't fit this repo's layout. |
| `f6-suspect-model-detected` | medium | `:audit` F6 fired the suspect-model sub-finding (model id not in bundled known-models list AND not in `config.audit.f6.modelIdExceptions`). Medium confidence — user may have a legitimate model id that the bundled list hasn't caught up to yet. Surface the candidate id + invite user to add to exceptions or update the bundled list. If context7 was unavailable when the lookup ran, confidence is lower; if context7 confirmed not-in-published-list, confidence is high. |
| `consolidated-diff-closes-multiple-findings` | positive | `:remediate` emitted a consolidated Category C diff that closed F10 + F11 (and optionally F12-high) in a single edit instead of two/three diffs. Positive signal — the consolidation-rules heuristic correctly recognized the same call site + structural overlap and saved the user from reviewing duplicate diffs. Validates `consolidation-rules.md` for this app. |
| `f12-severity-no-longer-degraded-by-composer-multiplicity` | positive | After v0.7 F12 severity-decoupling, a finding that v0.6 would have degraded from critical → high purely because of composer multiplicity now stays critical (apiParameter detection succeeded; multiplicity is metadata, not severity input). Positive signal — the v0.7 decoupling correctly separates detection ambiguity from composition shape. Lift this case into the smell-rubric example if the pattern recurs. |
