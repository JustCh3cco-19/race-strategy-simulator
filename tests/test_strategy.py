"""Tests for strategy validation rules."""

import pytest

from race_strategy.models.strategy import PitStop, Strategy


def test_strategy_rejects_duplicate_stop_laps() -> None:
    """Reject two pit stops scheduled for the same lap."""
    with pytest.raises(ValueError, match="strictly increasing"):
        Strategy(
            starting_compound="medium",
            stops=[
                PitStop(lap=10, compound="hard"),
                PitStop(lap=10, compound="soft"),
            ],
        )
