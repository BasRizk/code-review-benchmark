"""Tests for llm/prompts.py: the extraction prompt counts a restated finding once."""

from __future__ import annotations

from llm.prompts import EXTRACT_BOT_SUGGESTIONS


def _render() -> str:
    return EXTRACT_BOT_SUGGESTIONS.format(
        bot_username="reviewer[bot]",
        pr_title="Add retry",
        pr_author="dev",
        repo_name="org/repo",
        bot_comments="COMMENT C1 [INLINE_REVIEW_COMMENT path=src/app.py:42 timestamp=2026-07-01T12:00:00Z]\n...",
        commits_under_review="(no commits)",
    )


def test_extract_bot_suggestions_still_renders_with_all_placeholders() -> None:
    rendered = _render()

    assert "reviewer[bot]" in rendered
    assert "{" not in rendered
    assert "}" not in rendered


def test_extract_bot_suggestions_counts_restated_findings_once() -> None:
    rendered = _render()

    assert "Extract each finding once." in rendered
    assert "A restatement is not a new finding" in rendered
    assert "Two different issues in the same file or on the same line are\nstill two findings." in rendered
    assert rendered.index("Extract each finding once.") < rendered.index("=== Bot Review Comments ===")
