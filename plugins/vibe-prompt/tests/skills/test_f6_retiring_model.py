"""
v0.8 — contract tests for the known-models refresh and the F6-retiring-model
sub-finding.

The Retirement dates tables in known-models.md are data the audit agent reads,
so these tests parse them and replay the documented severity rule against the
two real positives named in the rubric (audit date 2026-09-22). If the table
and the rubric's worked examples ever disagree, this fails.

Asserts:
  1. known-models.md last-updated stamp is 2026-09-30 and cites sources
  2. Current Anthropic ids + Bedrock form + the three Gemini ids are listed
  2b. v0.8.1: claude-sonnet-5-5 is Current (+ Bedrock form), claude-sonnet-5
      is Legacy, and no Haiku 5.x id is listed
  3. Never-published claude-sonnet-4-7 / claude-haiku-4-6 are not list entries
  4. Retirement dates section parses; key rows carry the documented dates
     (v0.8.1: claude-sonnet-4-5 is scheduled 2026-11-30, claude-sonnet-5-5
     floor 2027-09-28, claude-sonnet-5 floor 2027-06-30 unchanged)
  5. Severity replay: 6deux6 haiku-4-5 -> medium, ClaudeProvider 3-5-sonnet -> high
  6. Rubric + SKILL wire F6-retiring-model (60-day window, evidence fields)
  7. modelIdExceptions does not suppress F6-retiring-model
"""

import datetime
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
AUDIT_SKILL = ROOT / "skills" / "audit" / "SKILL.md"
RUBRIC = ROOT / "skills" / "audit" / "references" / "smell-rubric-f1-f13.md"
KNOWN_MODELS = ROOT / "skills" / "audit" / "references" / "known-models.md"

AUDIT_DATE = datetime.date(2026, 9, 22)


def _bullets(text):
    """Model ids listed as `- `id`` bullet entries (comments excluded)."""
    return set(re.findall(r"^- `([^`]+)`", text, re.M))


def _anthropic_group(text, heading):
    """Bullets under one list heading inside the Anthropic section."""
    start = text.find("## Anthropic (Claude)")
    end = text.find("\n## ", start + 1)
    section = text[start:end]
    gstart = section.find(heading)
    gend = section.find("\n\n", section.find("\n- ", gstart) + 1)
    return _bullets(section[gstart:gend if gend > 0 else len(section)])


def _strip(model_id):
    """Suffix-strip per known-models.md Detection rules."""
    mid = model_id.lower()
    mid = re.sub(r"\[[^\]]*\]$", "", mid)
    mid = re.sub(r"@\d{8}$", "", mid)
    mid = re.sub(r"-\d{8}$", "", mid)
    return mid


def _retirement_rows(text):
    start = text.find("## Retirement dates")
    end = text.find("\n## ", start + 1)
    section = text[start:end]
    rows = {}
    for line in section.splitlines():
        m = re.match(r"^\| `([^`]+)` \| .* \| (\d{4}-\d{2}-\d{2}) \| (retired|scheduled|floor) \|$", line)
        if m:
            rows[m.group(1)] = (datetime.date.fromisoformat(m.group(2)), m.group(3))
    return rows


def _severity(model_id, rows, today=AUDIT_DATE):
    """Replay of the rubric's F6-retiring-model rule. None = no finding."""
    key = _strip(model_id)
    if key not in rows:
        return None
    date, kind = rows[key]
    days = (date - today).days
    if kind == "retired" or (kind == "scheduled" and days <= 0):
        return "high"
    if kind == "floor" and days <= 0:
        return "medium"
    if 0 < days <= 60:
        return "medium"
    return None


class TestKnownModelsRefresh(unittest.TestCase):

    def setUp(self):
        self.text = KNOWN_MODELS.read_text(encoding="utf-8")
        self.bullets = _bullets(self.text)

    def test_last_updated_stamp(self):
        self.assertIn("**Last-updated:** 2026-10-01", self.text)

    def test_sources_cited(self):
        for url in [
            "https://platform.claude.com/docs/en/models/overview",
            "https://platform.claude.com/docs/en/about-claude/model-deprecations",
            "https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5",
            "https://ai.google.dev/gemini-api/docs/models",
            "https://ai.google.dev/gemini-api/docs/deprecations",
        ]:
            self.assertIn(url, self.text)

    def test_current_anthropic_ids(self):
        for mid in [
            "claude-opus-5-5", "claude-fable-5-1", "claude-fable-5",
            "claude-opus-5", "claude-sonnet-5-5", "claude-sonnet-5",
            "claude-opus-4-8", "claude-haiku-4-5",
            "anthropic.claude-opus-5-5", "anthropic.claude-sonnet-5-5",
        ]:
            self.assertIn(mid, self.bullets, f"{mid} must be a known-models entry")

    def test_sonnet_5_5_is_current_and_sonnet_5_is_legacy(self):
        current = _anthropic_group(self.text, "Current (models overview")
        legacy = _anthropic_group(self.text, "Legacy, still available:")
        self.assertIn("claude-sonnet-5-5", current)
        self.assertNotIn("claude-sonnet-5", current)
        self.assertIn("claude-sonnet-5", legacy)
        self.assertNotIn("claude-sonnet-5-5", legacy)

    def test_no_haiku_5_x_listed(self):
        # Haiku 4.5 is still the current Haiku on 2026-09-30; a Haiku 5.x id
        # would be an unpublished entry.
        for mid in self.bullets:
            self.assertFalse(mid.startswith("claude-haiku-5"), f"{mid} is not published")

    def test_unpublished_ids_removed(self):
        for mid in ["claude-sonnet-4-7", "claude-haiku-4-6"]:
            self.assertNotIn(mid, self.bullets, f"{mid} was never published")

    def test_gemini_false_suspects_added(self):
        for mid in ["gemini-2.5-flash-image", "gemini-3.5-flash", "gemini-3-pro-preview"]:
            self.assertIn(mid, self.bullets)


class TestRetirementTable(unittest.TestCase):

    def setUp(self):
        self.rows = _retirement_rows(KNOWN_MODELS.read_text(encoding="utf-8"))

    def test_section_parses(self):
        self.assertGreaterEqual(len(self.rows), 20)

    def test_documented_dates(self):
        expected = {
            "claude-sonnet-4-5": ("2026-11-30", "scheduled"),
            "claude-haiku-4-5": ("2026-10-15", "floor"),
            "claude-opus-4-5": ("2026-11-24", "floor"),
            "claude-sonnet-5": ("2027-06-30", "floor"),
            "claude-sonnet-5-5": ("2027-09-28", "floor"),
            "claude-3-5-sonnet": ("2025-10-28", "retired"),
            "claude-opus-4-1": ("2026-08-05", "retired"),
            "gemini-2.5-flash-image": ("2026-10-02", "scheduled"),
        }
        for mid, (date, kind) in expected.items():
            self.assertIn(mid, self.rows)
            self.assertEqual(self.rows[mid], (datetime.date.fromisoformat(date), kind), mid)

    def test_served_models_have_no_retired_row(self):
        # gemini-3-pro-preview carried a "retired 2026-03-09" row through 0.8.1
        # while Google served it live (verified 2026-10-01 against the models
        # endpoint). A retired row on a served model fires F6-retiring-model at
        # high on every app that pins it, so the row must stay gone.
        self.assertNotIn("gemini-3-pro-preview", self.rows)

    def test_real_positive_6deux6_is_medium(self):
        # 6deux6/config.json:3
        self.assertEqual(_severity("claude-haiku-4-5-20251001", self.rows), "medium")

    def test_real_positive_claude_provider_is_high(self):
        # Project-626Labs-1/services/ai/ClaudeProvider.ts:24
        self.assertEqual(_severity("claude-3-5-sonnet-20241022", self.rows), "high")

    def test_outside_window_no_finding(self):
        # Opus 4.5 floor is 63 days out on the audit date.
        self.assertIsNone(_severity("claude-opus-4-5-20251101", self.rows))
        self.assertIsNone(_severity("claude-opus-5-5", self.rows))
        self.assertIsNone(_severity("claude-sonnet-5-5", self.rows))

    def test_sonnet_4_5_scheduled_fires_inside_window(self):
        # Deprecated 2026-09-30 with retirement 2026-11-30: 61 days out on
        # the announcement day (no finding), medium once inside 60 days,
        # high on and after the retirement date.
        self.assertIsNone(_severity("claude-sonnet-4-5-20250929", self.rows,
                                    today=datetime.date(2026, 9, 30)))
        self.assertEqual(_severity("claude-sonnet-4-5-20250929", self.rows,
                                   today=datetime.date(2026, 10, 1)), "medium")
        self.assertEqual(_severity("claude-sonnet-4-5-20250929", self.rows,
                                   today=datetime.date(2026, 11, 30)), "high")

    def test_unlisted_no_finding(self):
        self.assertIsNone(_severity("gemini-3.5-flash", self.rows))


class TestF6RetiringWiring(unittest.TestCase):

    def setUp(self):
        self.rubric = RUBRIC.read_text(encoding="utf-8")
        start = self.rubric.find("## F6-retiring-model")
        end = self.rubric.find("\n## ", start + 1)
        self.section = self.rubric[start:end] if start >= 0 else ""
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")

    def test_rubric_section(self):
        self.assertTrue(self.section, "rubric must carry ## F6-retiring-model")

    def test_sixty_day_window(self):
        self.assertIn("60 days", self.section)

    def test_evidence_fields(self):
        for field in ["modelValue", "occurrences", "retirementDate", "daysRemaining"]:
            self.assertIn(field, self.section)

    def test_worked_examples(self):
        self.assertIn("6deux6/config.json:3", self.section)
        self.assertIn("ClaudeProvider.ts:24", self.section)

    def test_exceptions_do_not_suppress(self):
        self.assertIn("does NOT suppress F6-retiring-model", self.section)

    def test_skill_step(self):
        self.assertIn('id: "F6-retiring-model"', self.skill)
        self.assertIn("Retirement dates", self.skill)
        self.assertIn("does NOT suppress F6-retiring-model", self.skill)


if __name__ == "__main__":
    unittest.main()
