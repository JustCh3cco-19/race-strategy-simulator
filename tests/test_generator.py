"""Tests for legal strategy generation."""

from pathlib import Path

from race_strategy.config import load_race_config
from race_strategy.strategy.generator import generate_strategies


def test_generator_respects_stint_constraints() -> None:
    """Generate strategies whose stints satisfy configured tyre limits."""
    race = load_race_config(Path("configs/example_race.yaml"))
    strategies = list(
        generate_strategies(race, min_stops=1, max_stops=1, pit_window=10)
    )

    assert strategies
    assert all(len(strategy.stops) == 1 for strategy in strategies)
    assert all(strategy.stops[0].lap % 10 == 0 for strategy in strategies)


def test_generator_rejects_invalid_bounds() -> None:
    """Reject an invalid stop range before enumerating combinations."""
    race = load_race_config(Path("configs/example_race.yaml"))

    try:
        list(generate_strategies(race, min_stops=2, max_stops=1))
    except ValueError as error:
        assert "stop bounds" in str(error)
    else:
        raise AssertionError("invalid stop bounds should raise ValueError")


def test_generator_never_emits_first_lap_stop() -> None:
    """Keep generated strategies valid when the pit window is one lap."""
    race = load_race_config(Path("configs/example_race.yaml"))
    strategies = list(generate_strategies(race, min_stops=1, max_stops=1, pit_window=1))

    assert strategies
    assert all(strategy.stops[0].lap > 1 for strategy in strategies)
    for strategy in strategies:
        race.validate_strategy(strategy)
