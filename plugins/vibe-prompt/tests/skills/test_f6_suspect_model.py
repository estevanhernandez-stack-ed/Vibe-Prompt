"""
Task 21 — TDD tests for F6 suspect-model sub-finding (v0.7).

Background: v0.1 removed an early "suspect model" sub-finding from F6 because
the bundled known-models list went stale fast and produced false positives.
v0.7 revives it with two improvements:
  - A bundled known-models list at references/known-models.md with a
    last-updated stamp (the previous failure mode acknowledged)
  - Confidence ladder: context7 lookup available → high (vendor-confirmed
    not-in-published-list); context7 unavailable → medium (bundled-list-only)
  - Config-driven escape hatch via `audit.f6.modelIdExceptions[]` so users
    can suppress the finding on intentional / pre-release / vendor-internal
    model IDs.

The sub-finding's id is `F6-suspect-model` (distinct from the existing
consolidation finding which keeps id `F6`).

Asserts:
  1. references/known-models.md exists with sections + last-updated stamp
  2. audit/SKILL.md adds an F6 suspect-model detection step
  3. rubric documents the F6-suspect-model sub-finding with id, severity,
     confidence ladder, and exception-list escape
  4. context7-aware confidence is documented (high vs medium)
  5. `audit.f6.modelIdExceptions` config field is referenced in SKILL or rubric
"""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
AUDIT_SKILL = ROOT / "skills" / "audit" / "SKILL.md"
RUBRIC = ROOT / "skills" / "audit" / "references" / "smell-rubric-f1-f13.md"
KNOWN_MODELS = ROOT / "skills" / "audit" / "references" / "known-models.md"


class TestF6SuspectModel(unittest.TestCase):

    def test_known_models_reference_exists(self):
        """references/known-models.md must exist."""
        self.assertTrue(
            KNOWN_MODELS.exists(),
            "references/known-models.md must exist (bundled known-models list)"
        )

    def test_known_models_has_last_updated(self):
        """known-models.md must include a last-updated stamp."""
        if not KNOWN_MODELS.exists():
            self.fail("known-models.md missing")
        body = KNOWN_MODELS.read_text(encoding="utf-8").lower()
        has_stamp = (
            "last-updated" in body
            or "last updated" in body
            or "updated:" in body
        )
        self.assertTrue(
            has_stamp,
            "known-models.md must carry a last-updated stamp"
        )

    def test_known_models_lists_at_least_one_vendor(self):
        """known-models.md must enumerate at least one vendor's model id list."""
        if not KNOWN_MODELS.exists():
            self.fail("known-models.md missing")
        body = KNOWN_MODELS.read_text(encoding="utf-8").lower()
        # At least one of these vendors named
        has_vendor = any(v in body for v in ["google", "gemini", "anthropic", "claude", "openai", "gpt"])
        self.assertTrue(has_vendor, "known-models.md must enumerate at least one vendor's models")

    def test_skill_documents_f6_suspect_model_step(self):
        """audit/SKILL.md must add an F6 suspect-model detection step."""
        skill = AUDIT_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "F6-suspect-model",
            skill,
            "audit/SKILL.md must add F6-suspect-model detection step"
        )

    def test_rubric_documents_f6_suspect_model_section(self):
        """rubric must add an F6-suspect-model sub-finding section."""
        rubric = RUBRIC.read_text(encoding="utf-8")
        self.assertIn(
            "F6-suspect-model",
            rubric,
            "smell-rubric must add F6-suspect-model sub-finding section"
        )

    def test_rubric_documents_confidence_ladder(self):
        """rubric must document context7-aware confidence ladder (high vs medium)."""
        rubric = RUBRIC.read_text(encoding="utf-8").lower()
        has_context7 = "context7" in rubric
        has_levels = "high" in rubric and "medium" in rubric
        self.assertTrue(
            has_context7 and has_levels,
            "rubric must document context7 confidence ladder (high w/ context7, medium without)"
        )

    def test_config_exception_field_referenced(self):
        """SKILL or rubric must reference audit.f6.modelIdExceptions config field."""
        combined = AUDIT_SKILL.read_text(encoding="utf-8") + RUBRIC.read_text(encoding="utf-8")
        self.assertIn(
            "modelIdExceptions",
            combined,
            "audit.f6.modelIdExceptions config field must be referenced for escape-hatch behavior"
        )

    def test_severity_default_documented(self):
        """rubric must document severity default (medium for F6-suspect-model)."""
        rubric = RUBRIC.read_text(encoding="utf-8")
        start = rubric.find("F6-suspect-model")
        section = rubric[start: start + 2000] if start >= 0 else ""
        lowered = section.lower()
        has_severity = "severity" in lowered and "medium" in lowered
        self.assertTrue(
            has_severity,
            "rubric F6-suspect-model section must declare severity default (medium)"
        )

    def test_v07_reference_for_revival(self):
        """rubric or SKILL must reference v0.7 for the revival."""
        combined = AUDIT_SKILL.read_text(encoding="utf-8") + RUBRIC.read_text(encoding="utf-8")
        self.assertIn(
            "v0.7",
            combined,
            "F6-suspect-model revival must be tagged v0.7"
        )


if __name__ == "__main__":
    unittest.main()
