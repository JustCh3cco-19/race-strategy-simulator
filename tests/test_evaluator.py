"""Tests for strategy evaluation and ranking."""

from pathlib import Path

import pytest

from race_strategy.analytics.metrics import summarize_results
from race_strategy.config import load_race_config
from race_strategy.models.strategy import Strategy
from race_strategy.strategy.evaluator import (
    format_strategy,
    rank_strategies,
    rank_strategies_common_random_numbers,
)


def test_rank_strategies_is_sorted_and_reproducible() -> None:
    """Rank strategies by mean time with deterministic results."""
    race = load_race_config(Path("configs/example_race.yaml"))
    strategies = [
        Strategy(starting_compound="soft"),
        Strategy(starting_compound="hard"),
    ]

    ranked = rank_strategies(race, strategies, runs=3, seed=11)

    assert ranked[0].summary.mean <= ranked[1].summary.mean
    assert ranked[0].summary.average_pit_stops == 0.0
    assert ranked == rank_strategies(race, strategies, runs=3, seed=11)


def test_format_strategy_is_compact() -> None:
    """Format a strategy for reuse with the CLI."""
    strategy = Strategy(starting_compound="medium")

    assert format_strategy(strategy) == "medium"


def test_common_random_numbers_probabilities_sum_to_one() -> None:
    """Compute fastest-strategy probabilities from shared scenarios."""
    race = load_race_config(Path("configs/example_race.yaml"))
    strategies = [
        Strategy(starting_compound="soft"),
        Strategy(starting_compound="hard"),
    ]

    ranked = rank_strategies_common_random_numbers(race, strategies, runs=4, seed=5)

    assert sum(item.probability_fastest for item in ranked) == 1.0


def test_rank_reports_retirement_rate() -> None:
    """Expose DNF frequency when vehicle reliability is zero."""
    race = load_race_config(Path("configs/example_race.yaml"))
    unreliable_race = race.model_copy(
        update={"car": race.car.model_copy(update={"reliability": 0.0})}
    )

    ranked = rank_strategies(unreliable_race, [Strategy(starting_compound="medium")], 3)

    assert ranked[0].summary.retirement_rate == 1.0


def test_metrics_reject_empty_results() -> None:
    """Require at least one result for aggregate analytics."""
    with pytest.raises(ValueError, match="at least one race result"):
        summarize_results([])
