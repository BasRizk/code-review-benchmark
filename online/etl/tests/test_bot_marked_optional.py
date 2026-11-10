"""Tests for the bot_marked_optional field: schema default, prompt wording, reporting split."""

from __future__ import annotations

from llm.prompts import EXTRACT_BOT_SUGGESTIONS
from llm.schemas import BotSuggestion
from llm.schemas import BotSuggestionsResponse
from pipeline.analyze import _bot_marked_optional_counts


def test_bot_marked_optional_defaults_to_false() -> None:
    s = BotSuggestion(issue_id="S1", description="d", category="bug")

    assert s.bot_marked_optional is False
    assert s.model_dump()["bot_marked_optional"] is False


def test_bot_marked_optional_round_trips_through_json() -> None:
    r = BotSuggestionsResponse(
        suggestions=[BotSuggestion(issue_id="S1", description="d", category="style", bot_marked_optional=True)]
    )

    assert BotSuggestionsResponse.model_validate_json(r.model_dump_json()).suggestions[0].bot_marked_optional is True


def test_older_stored_suggestions_without_the_field_still_validate() -> None:
    s = BotSuggestion.model_validate({"issue_id": "S1", "description": "d", "category": "bug"})

    assert s.bot_marked_optional is False


def test_extract_prompt_asks_for_the_bots_own_label_only() -> None:
    rendered = EXTRACT_BOT_SUGGESTIONS.format(
        bot_username="reviewer[bot]",
        pr_title="t",
        pr_author="a",
        repo_name="org/repo",
        bot_comments="(no bot comments)",
        commits_under_review="(no commits)",
    )

    assert "bot_marked_optional" in rendered
    assert "Do not infer it from severity or tone." in rendered
    assert "{" not in rendered


def test_bot_marked_optional_counts_split_matched_and_unmatched() -> None:
    suggestions = [
        {"issue_id": "S1", "bot_marked_optional": False},
        {"issue_id": "S2", "bot_marked_optional": True},
        {"issue_id": "S3", "bot_marked_optional": True},
        {"issue_id": "S4"},  # stored before the field existed
    ]

    counts = _bot_marked_optional_counts(suggestions, {"S1", "S3"})

    assert counts == {
        "optional_suggestions": 2,
        "optional_matched": 1,
        "required_suggestions": 2,
        "required_matched": 1,
    }


def test_bot_marked_optional_counts_with_no_suggestions() -> None:
    assert _bot_marked_optional_counts([], set()) == {
        "optional_suggestions": 0,
        "optional_matched": 0,
        "required_suggestions": 0,
        "required_matched": 0,
    }
