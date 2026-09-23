"""
v0.8 validation fixes — F14 candidate detection and model resolution.

Asserts (rubric §F14 and audit SKILL step 4g agree):
  1. Raw HTTP detection keys on the api.anthropic.com/v1/messages URL, not the
     callee: fetchImpl, got, undici, Roblox HttpService:RequestAsync qualify
  2. Dynamic `await import('@anthropic-ai/sdk')` is named explicitly
  3. No language restriction on candidate files
  4. "Older" spans every non-5.5/5.1-era Claude family (Sonnet 4, Claude 3.x)
  5. Mixed `options?.model || 'literal'` resolves to unresolved
  6. Retired older pins use the retired line (not the latent copy), keep F14
     medium, and cross-reference F6-retiring-model
  7. Replay: the validation positives resolve to the documented severities
"""

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
AUDIT_SKILL = ROOT / "skills" / "audit" / "SKILL.md"
RUBRIC = ROOT / "skills" / "audit" / "references" / "smell-rubric-f1-f13.md"
KNOWN_MODELS = ROOT / "skills" / "audit" / "references" / "known-models.md"

RETIRED_LINE = (
    "The pinned model `{modelValue}` is already retired (see F6-retiring-model), "
    "so this call fails today regardless; fix both together."
)


def _rubric_f14():
    text = RUBRIC.read_text(encoding="utf-8")
    start = text.find("## F14")
    return text[start:text.find("\n## ", start + 1)]


def _skill_4g():
    text = AUDIT_SKILL.read_text(encoding="utf-8")
    start = text.find("4g. **F14")
    return text[start:text.find("\n5. ", start)]


class TestCandidateDetection(unittest.TestCase):

    def setUp(self):
        self.surfaces = {"rubric": _rubric_f14(), "skill": _skill_4g()}

    def test_url_keyed_not_callee(self):
        for name, text in self.surfaces.items():
            self.assertIn("api.anthropic.com/v1/messages", text, name)
            self.assertIn("not the callee", text, name)
            for client in ["fetchImpl", "got", "undici", "HttpService:RequestAsync"]:
                self.assertIn(client, text, f"{name}: {client}")

    def test_dynamic_import_named(self):
        for name, text in self.surfaces.items():
            self.assertIn("await import('@anthropic-ai/sdk')", text, name)

    def test_no_language_restriction(self):
        for name, text in self.surfaces.items():
            self.assertIn("No language restriction", text, name)


class TestModelResolution(unittest.TestCase):

    def setUp(self):
        self.surfaces = {"rubric": _rubric_f14(), "skill": _skill_4g()}

    def test_older_spans_families(self):
        for name, text in self.surfaces.items():
            self.assertIn("Sonnet 4", text, name)
            self.assertIn("Claude 3.x", text, name)
            self.assertIn("in any family", text, name)

    def test_mixed_expression_unresolved(self):
        for name, text in self.surfaces.items():
            self.assertIn("options?.model || '", text, name)
            self.assertRegex(text, r"mixed expression.{0,80}`unresolved`", name)

    def test_retired_pin_line(self):
        for name, text in self.surfaces.items():
            self.assertIn(RETIRED_LINE, text, name)
            self.assertIn("F6-retiring-model", text, name)

    def test_retired_pin_keeps_medium(self):
        self.assertIn("Keep the F14 severity at **medium**", self.surfaces["rubric"])
        self.assertIn("keep F14 at medium", self.surfaces["skill"])

    def test_latent_line_conditioned_on_not_retired(self):
        self.assertIn("older-pinned and the model is NOT retired", self.surfaces["rubric"])


def _retired_ids():
    text = KNOWN_MODELS.read_text(encoding="utf-8")
    return {
        m.group(1)
        for m in re.finditer(r"^\| `([^`]+)` \| .* \| \d{4}-\d{2}-\d{2} \| retired \|$", text, re.M)
    }


def _resolve(expr, retired):
    """Replay of step 3. Returns (modelResolution, severity, retiredPin)."""
    lit = re.fullmatch(r"['\"]([^'\"]+)['\"]", expr.strip())
    if not lit:
        return ("unresolved", "high", False)
    mid = re.sub(r"-\d{8}$", "", lit.group(1).lower())
    if mid in {"claude-opus-5-5", "claude-fable-5-1"}:
        return ("resolved", "high", False)
    return ("older-pinned", "medium", mid in retired)


class TestReplay(unittest.TestCase):

    def setUp(self):
        self.retired = _retired_ids()

    def test_626labs_free_string_model_is_unresolved_high(self):
        # functions/src/domains/ai/index.ts:64 passes `model` from a z.string()
        self.assertEqual(_resolve("model", self.retired), ("unresolved", "high", False))

    def test_mixed_fallback_is_unresolved(self):
        self.assertEqual(
            _resolve("options?.model || 'claude-3-5-sonnet-20241022'", self.retired)[0],
            "unresolved",
        )

    def test_quizshow_retired_pin_is_medium_with_retired_line(self):
        # claude-question-gen.ts:282 pins claude-sonnet-4-20250514
        self.assertEqual(
            _resolve("'claude-sonnet-4-20250514'", self.retired),
            ("older-pinned", "medium", True),
        )

    def test_live_older_pin_is_latent(self):
        self.assertEqual(
            _resolve("'claude-opus-5'", self.retired),
            ("older-pinned", "medium", False),
        )


if __name__ == "__main__":
    unittest.main()
