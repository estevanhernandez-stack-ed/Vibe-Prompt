"""
Task 25 (v0.5) — TDD tests for audit/SKILL.md F10/F11/F12 origin filtering.

In v0.5, F10/F11/F12 detection prose must filter
`templatedVars[].origin === "user-controlled"` BEFORE applying detection.
When a candidate var is excluded because it's system-injected, the audit
SKILL prose must declare an `originFilteredOut: true` annotation on the
finding (or the skipped detection).

Asserts:
  1. audit/SKILL.md F10 detection step references `origin` filter
  2. audit/SKILL.md F11 detection step references `origin` filter
  3. audit/SKILL.md F12 detection step references `origin` filter
  4. audit/SKILL.md declares the `originFilteredOut` annotation
  5. audit/SKILL.md prose treats the filter as an additional pre-step
     (not a replacement of v0.4 detection)
  6. The system-injected vars are excluded from the candidate set
  7. v0.4 F10/F11/F12 detection prose is preserved (no regression)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
AUDIT_SKILL = SKILLS_DIR / "audit" / "SKILL.md"


class TestAuditOriginFiltering(unittest.TestCase):

    def setUp(self):
        self.content = AUDIT_SKILL.read_text(encoding="utf-8")
        self.content_lower = self.content.lower()

    # ------------------------------------------------------------------ #
    # 1. F10 detection references origin filter                           #
    # ------------------------------------------------------------------ #

    def test_f10_references_origin_filter(self):
        # Find F10 *detection* section (the 4c step), not the first F10 mention
        f10_idx = self.content.find("4c. **F10")
        self.assertGreater(
            f10_idx, -1,
            "Audit SKILL must have step 4c with F10 detection prose"
        )
        f10_section = self.content[f10_idx:f10_idx + 3500]
        has_origin = (
            "origin" in f10_section
            or "user-controlled" in f10_section
            or "system-injected" in f10_section
        )
        self.assertTrue(
            has_origin,
            "F10 detection prose (step 4c) must reference `origin` / "
            "user-controlled filter (v0.5)"
        )

    # ------------------------------------------------------------------ #
    # 2. F11 detection references origin filter                           #
    # ------------------------------------------------------------------ #

    def test_f11_references_origin_filter(self):
        f11_idx = self.content.find("4d. **F11")
        self.assertGreater(
            f11_idx, -1,
            "Audit SKILL must have step 4d with F11 detection prose"
        )
        f11_section = self.content[f11_idx:f11_idx + 2500]
        has_origin = (
            "origin" in f11_section
            or "user-controlled" in f11_section
            or "system-injected" in f11_section
            or "pre-filter" in f11_section
        )
        self.assertTrue(
            has_origin,
            "F11 detection prose (step 4d) must reference origin filter "
            "(directly or via F10 prereq) in v0.5"
        )

    # ------------------------------------------------------------------ #
    # 3. F12 detection references origin filter                           #
    # ------------------------------------------------------------------ #

    def test_f12_references_origin_filter(self):
        f12_idx = self.content.find("4e. **F12")
        self.assertGreater(
            f12_idx, -1,
            "Audit SKILL must have step 4e with F12 detection prose"
        )
        f12_section = self.content[f12_idx:f12_idx + 3000]
        has_origin = (
            "origin" in f12_section
            or "user-controlled" in f12_section
            or "system-injected" in f12_section
            or "pre-filter" in f12_section
        )
        self.assertTrue(
            has_origin,
            "F12 detection prose (step 4e) must reference origin filter "
            "(directly or via F10 prereq) in v0.5"
        )

    # ------------------------------------------------------------------ #
    # 4. originFilteredOut annotation declared                            #
    # ------------------------------------------------------------------ #

    def test_origin_filtered_out_annotation_declared(self):
        self.assertIn(
            "originFilteredOut",
            self.content,
            "audit/SKILL.md must declare the `originFilteredOut` annotation "
            "for vars excluded due to system-injected detection"
        )

    # ------------------------------------------------------------------ #
    # 5. Origin filter is an ADDITIONAL pre-step (not a replacement)      #
    # ------------------------------------------------------------------ #

    def test_origin_filter_is_pre_step(self):
        """The filter must be an additional pre-step, not a replacement of
        v0.4 detection. v0.4 detection rules (heuristic regex, defense phrases,
        composer.json layer order) must still appear in the prose."""
        # All three v0.4 hallmarks must remain
        self.assertIn("user-origin heuristics", self.content,
                      "v0.4 F10 user-origin heuristic must remain in prose")
        self.assertIn("defense", self.content_lower,
                      "v0.4 F11 defense-phrase prose must remain")
        self.assertIn("composition order", self.content_lower,
                      "v0.4 F12 composition-order prose must remain")

    # ------------------------------------------------------------------ #
    # 6. system-injected vars are excluded from candidate set             #
    # ------------------------------------------------------------------ #

    def test_system_injected_vars_excluded(self):
        # The prose must state the skip / exclude behavior
        has_skip = (
            "skip" in self.content_lower
            or "exclude" in self.content_lower
            or "filter out" in self.content_lower
            or "filter" in self.content_lower
        )
        self.assertTrue(
            has_skip,
            "audit/SKILL.md must declare that system-injected vars are "
            "skipped / excluded from F10-F12 detection"
        )

    # ------------------------------------------------------------------ #
    # 7. v0.4 detection prose preserved (no regression)                   #
    # ------------------------------------------------------------------ #

    def test_v04_finding_steps_still_present(self):
        # All v0.4 numbered steps for F10/F11/F12 must remain
        for marker in ["4c. **F10", "4d. **F11", "4e. **F12"]:
            self.assertIn(
                marker,
                self.content,
                f"v0.4 marker '{marker}' must be preserved in audit/SKILL.md"
            )


if __name__ == "__main__":
    unittest.main()
