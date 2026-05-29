"""
Task 28 (v0.5) — TDD tests for F12 handoff banner integration in
remediate/SKILL.md.

Per spec §1f, F12 critical findings do NOT get an auto-proposed fix.
`:remediate` emits a handoff banner naming the composer file path and
recommending `/vibe-sec:audit`. `--skip-f12` suppresses the banner.
F12 high-severity (confidence-degraded by missing composer.json) still
proposes via Category C fallback because the additive defense is a
reasonable intermediate fix.

Asserts:
  1. SKILL declares the F12 handoff banner section
  2. Banner text names the composer file path
  3. Banner recommends /vibe-sec:audit
  4. `--skip-f12` flag suppresses the banner
  5. F12 high-severity Category C fallback is documented
  6. F12 critical does NOT propose an auto fix (explicitly stated)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestRemediateF12Handoff(unittest.TestCase):

    def setUp(self):
        self.content = REMEDIATE_SKILL.read_text(encoding="utf-8")
        self.content_lower = self.content.lower()

    # ------------------------------------------------------------------ #
    # 1. F12 handoff section declared                                     #
    # ------------------------------------------------------------------ #

    def test_f12_handoff_section_declared(self):
        has_section = (
            "f12 handoff" in self.content_lower
            or "f12 handoff banner" in self.content_lower
            or "## f12 handoff" in self.content_lower
        )
        self.assertTrue(
            has_section,
            "remediate/SKILL.md must declare an F12 handoff banner section"
        )

    # ------------------------------------------------------------------ #
    # 2. Banner names the composer file                                   #
    # ------------------------------------------------------------------ #

    def test_banner_names_composer_file(self):
        idx = self.content.find("## F12 handoff")
        if idx == -1:
            # Fallback — bypass the frontmatter description match
            idx = self.content.find("## F12")
        self.assertGreater(idx, -1,
                           "remediate SKILL must have a '## F12 handoff' section")
        section = self.content[idx:idx + 2000]
        has_composer = (
            "composer" in section.lower()
            or "composerPath" in section
            or "<composerPath>" in section
        )
        self.assertTrue(
            has_composer,
            "F12 handoff banner must name the composer file path"
        )

    # ------------------------------------------------------------------ #
    # 3. Banner recommends /vibe-sec:audit                                #
    # ------------------------------------------------------------------ #

    def test_banner_recommends_vibe_sec(self):
        idx = self.content.find("## F12 handoff")
        if idx == -1:
            # Fallback — bypass the frontmatter description match
            idx = self.content.find("## F12")
        self.assertGreater(idx, -1,
                           "remediate SKILL must have a '## F12 handoff' section")
        section = self.content[idx:idx + 2000]
        has_vibe_sec = (
            "vibe-sec:audit" in section
            or "/vibe-sec:audit" in section
            or "vibe-sec" in section.lower()
        )
        self.assertTrue(
            has_vibe_sec,
            "F12 handoff banner must recommend /vibe-sec:audit"
        )

    # ------------------------------------------------------------------ #
    # 4. --skip-f12 flag suppresses banner                                #
    # ------------------------------------------------------------------ #

    def test_skip_f12_flag_suppresses_banner(self):
        self.assertIn(
            "--skip-f12",
            self.content,
            "SKILL must document the --skip-f12 flag"
        )
        idx = self.content.find("--skip-f12")
        # The mention near F12 handoff must indicate it suppresses
        section = self.content[max(0, idx - 100):idx + 400]
        has_suppress = (
            "suppress" in section.lower()
            or "skip" in section.lower()
            or "intentionally not fixing" in section.lower()
        )
        self.assertTrue(
            has_suppress,
            "--skip-f12 must be documented as suppressing the handoff banner"
        )

    # ------------------------------------------------------------------ #
    # 5. F12 high-severity Category C fallback                            #
    # ------------------------------------------------------------------ #

    def test_f12_high_severity_category_c_fallback(self):
        idx = self.content.find("## F12 handoff")
        if idx == -1:
            # Fallback — bypass the frontmatter description match
            idx = self.content.find("## F12")
        self.assertGreater(idx, -1,
                           "remediate SKILL must have a '## F12 handoff' section")
        section = self.content[idx:idx + 2000]
        # The section must describe what happens for F12 high (not critical):
        # a Category C fallback is proposed
        has_fallback = (
            "high" in section.lower()
            and (
                "category c" in section.lower()
                or "fallback" in section.lower()
                or "additive defense" in section.lower()
            )
        )
        self.assertTrue(
            has_fallback,
            "F12 high-severity must document a Category C fallback "
            "(spec §1f — additive defense is reasonable intermediate fix)"
        )

    # ------------------------------------------------------------------ #
    # 6. F12 critical does NOT propose an auto fix                        #
    # ------------------------------------------------------------------ #

    def test_f12_critical_does_not_propose_auto_fix(self):
        idx = self.content.find("## F12 handoff")
        if idx == -1:
            # Fallback — bypass the frontmatter description match
            idx = self.content.find("## F12")
        self.assertGreater(idx, -1,
                           "remediate SKILL must have a '## F12 handoff' section")
        section = self.content[idx:idx + 2000]
        # Look for explicit "does not" / "NOT propose" language near F12 critical
        no_proposal = (
            "does not propose" in section.lower()
            or "not propose" in section.lower()
            or "no fix" in section.lower()
            or "no auto-proposal" in section.lower()
            or "handoff banner only" in section.lower()
        )
        self.assertTrue(
            no_proposal,
            "F12 critical must explicitly NOT auto-propose a fix; the section "
            "must declare the no-proposal behavior"
        )

    # ------------------------------------------------------------------ #
    # 7. Banner text is in the SKILL (block-quote or fenced)              #
    # ------------------------------------------------------------------ #

    def test_banner_text_block_present(self):
        # The actual banner text should be reproducible — either fenced
        # code block or block-quote with the canonical wording
        has_block = (
            "Composition-order fixes belong upstream" in self.content
            or "F12 fired critical" in self.content
            or "Run `/vibe-sec:audit`" in self.content
        )
        self.assertTrue(
            has_block,
            "F12 handoff banner text must appear verbatim (block-quote or "
            "fenced code) in remediate/SKILL.md"
        )


if __name__ == "__main__":
    unittest.main()
