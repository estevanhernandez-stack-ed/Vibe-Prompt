r"""
Task 11 — TDD tests for var-origin Signal 2 (call-graph proximity).

Asserts:
  1. var-origin-detection.md declares Signal 2
  2. Pattern 2a — service-call assignment → system-injected (e.g., await KnowledgeService.get(...))
  3. Pattern 2b — form-input assignment → user-controlled (useState + setter)
  4. Pattern 2c — no traceable assignment → unknown (conservative: still fires F10)
  5. Confidence ≥0.80 for clear Pattern 2a/2b matches
  6. Confidence 0.40 for unknown / unresolved
  7. Signal 2 is applied when Signal 1 is inconclusive (no match OR conflict)
  8. Conservative fallback documented: unknown → treated as user-controlled for F10
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
VAR_ORIGIN_REF = SKILLS_DIR / "scan" / "references" / "var-origin-detection.md"


class TestVarOriginSignal2Documentation(unittest.TestCase):

    def setUp(self):
        self.ref = VAR_ORIGIN_REF.read_text(encoding="utf-8")

    def test_signal_2_declared(self):
        self.assertIn(
            "Signal 2",
            self.ref,
            "var-origin-detection.md must declare Signal 2",
        )

    def test_signal_2_call_graph_label(self):
        ref_lower = self.ref.lower()
        self.assertTrue(
            "call-graph" in ref_lower or "callgraph" in ref_lower or "call graph" in ref_lower,
            "Signal 2 must be labeled call-graph proximity",
        )

    def test_pattern_2a_service_call_documented(self):
        """Service-call assignment → system-injected. Example: await KnowledgeService.get(...)."""
        ref_lower = self.ref.lower()
        has_service = (
            "service" in ref_lower
            and ("await" in ref_lower or "knowledgeservice" in ref_lower)
        )
        self.assertTrue(
            has_service,
            "Signal 2 Pattern 2a must document service-call assignment pattern",
        )

    def test_pattern_2a_classifies_system_injected(self):
        # The 2a section should produce system-injected origin
        # Look for the example mapping or table row
        ref = self.ref
        # find first 'Pattern 2a' or 'service' section, look for system-injected nearby
        idx = ref.find("Pattern 2a")
        if idx < 0:
            idx = ref.lower().find("service-call")
        self.assertGreater(idx, 0, "Pattern 2a section must exist")
        section = ref[idx : idx + 2000]
        self.assertIn(
            "system-injected",
            section,
            "Pattern 2a section must classify as system-injected",
        )

    def test_pattern_2b_form_input_documented(self):
        """Form-input assignment → user-controlled. Example: useState + onChange."""
        ref_lower = self.ref.lower()
        has_form = (
            "useState" in self.ref
            or "form" in ref_lower
        ) and ("e.target.value" in self.ref or "onChange" in self.ref or "request.body" in self.ref)
        self.assertTrue(
            has_form,
            "Signal 2 Pattern 2b must document form-input assignment pattern",
        )

    def test_pattern_2b_classifies_user_controlled(self):
        ref = self.ref
        idx = ref.find("Pattern 2b")
        if idx < 0:
            idx = ref.lower().find("form-input")
        self.assertGreater(idx, 0, "Pattern 2b section must exist")
        section = ref[idx : idx + 2000]
        self.assertIn(
            "user-controlled",
            section,
            "Pattern 2b section must classify as user-controlled",
        )

    def test_confidence_080_for_clear_match(self):
        """Confidence ≥0.80 for clear Pattern 2a/2b match."""
        has_080 = "0.80" in self.ref or "0.8" in self.ref
        self.assertTrue(
            has_080,
            "Confidence ≥0.80 for clear Signal 2 match must be declared",
        )

    def test_confidence_040_for_unknown(self):
        """Confidence 0.40 for unresolved cases."""
        has_040 = "0.40" in self.ref or "0.4" in self.ref
        self.assertTrue(
            has_040,
            "Confidence 0.40 for unresolved cases must be declared",
        )

    def test_signal_2_applied_when_signal_1_inconclusive(self):
        """Signal 2 fires when Signal 1 is inconclusive."""
        ref_lower = self.ref.lower()
        has_chain = (
            "signal 1" in ref_lower
            and ("inconclusive" in ref_lower or "conflict" in ref_lower or "fall through" in ref_lower or "fall-through" in ref_lower or "defer to signal 2" in ref_lower)
        )
        self.assertTrue(
            has_chain,
            "Reference must document Signal 2 firing when Signal 1 is inconclusive",
        )

    def test_conservative_fallback_documented(self):
        """Unknown → treated as user-controlled for F10 purposes."""
        ref_lower = self.ref.lower()
        has_fallback = (
            "conservative" in ref_lower
            and "user-controlled" in self.ref
            and "f10" in ref_lower
        )
        self.assertTrue(
            has_fallback,
            "Conservative fallback (unknown → user-controlled for F10) must be documented",
        )


if __name__ == "__main__":
    unittest.main()
