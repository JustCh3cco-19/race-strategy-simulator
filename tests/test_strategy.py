"""Tests for strategy validation rules."""

from pathlib import Path

import pytest

from race_strategy.config import load_race_config
from race_strategy.models.strategy import PitStop, Strategy
from race_strategy.models.tyre import TyreCompound


def test_strategy_rejects_duplicate_stop_laps() -> None:
    """Reject two pit stops scheduled for the same lap."""
    # Duplicate laps would make the order of compound changes ambiguous.
    with pytest.raises(ValueError, match="strictly increasing"):
        Strategy(
            starting_compound="medium",
            stops=[
                PitStop(lap=10, compound="hard"),
                PitStop(lap=10, compound="soft"),
            ],
        )


def test_race_rejects_first_lap_pit_stop() -> None:
    """Reject a pit stop that would create a zero-lap opening stint."""
    race = load_race_config(Path("configs/example_race.yaml"))

    with pytest.raises(ValueError, match="after the first lap"):
        race.validate_strategy(
            Strategy(
                starting_compound="medium",
                stops=[PitStop(lap=1, compound="hard")],
            )
        )


def test_race_rejects_stint_shorter_than_compound_minimum() -> None:
    """Reject a manually supplied strategy violating stint constraints."""
    race = load_race_config(Path("configs/example_race.yaml"))
    tyres = dict(race.tyres)
    medium_data = tyres["medium"].model_dump()
    medium_data["minimum_stint"] = 10
    tyres["medium"] = TyreCompound(**medium_data)
    constrained_race = race.model_copy(update={"tyres": tyres})

    with pytest.raises(ValueError, match="shorter than minimum_stint"):
        constrained_race.validate_strategy(
            Strategy(
                starting_compound="medium",
                stops=[PitStop(lap=5, compound="hard")],
            )
        )
