"""Evaluation and ranking of generated strategies."""

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from race_strategy.models.race import RaceConfig
from race_strategy.models.strategy import Strategy
from race_strategy.simulation.engine import simulate_race
from race_strategy.simulation.monte_carlo import SimulationSummary, monte_carlo


@dataclass(frozen=True)
class StrategyEvaluation:
    """Monte Carlo result associated with one strategy."""

    strategy: Strategy
    summary: SimulationSummary
    probability_fastest: float = 0.0


def rank_strategies(
    race: RaceConfig,
    strategies: Iterable[Strategy],
    runs: int,
    seed: int = 0,
) -> list[StrategyEvaluation]:
    """Evaluate strategies and sort them by ascending mean race time.

    Args:
        race: Race configuration used for every simulation.
        strategies: Strategies to evaluate.
        runs: Number of Monte Carlo runs per strategy.
        seed: Master seed; each strategy receives a deterministic derived seed.

    Returns:
        Evaluations sorted from fastest to slowest mean time.

    Raises:
        ValueError: If no strategies are supplied or ``runs`` is not positive.
    """
    strategy_list = list(strategies)
    if not strategy_list:
        raise ValueError("at least one strategy is required")
    if runs <= 0:
        raise ValueError("runs must be positive")
    evaluations = [
        StrategyEvaluation(strategy, monte_carlo(race, strategy, runs, seed + index))
        for index, strategy in enumerate(strategy_list)
    ]
    return sorted(evaluations, key=lambda evaluation: evaluation.summary.mean)


def rank_strategies_common_random_numbers(
    race: RaceConfig,
    strategies: Iterable[Strategy],
    runs: int,
    seed: int = 0,
) -> list[StrategyEvaluation]:
    """Rank strategies using identical random scenarios for every strategy.

    Shared seeds make the ``probability_fastest`` metric a paired comparison:
    each run represents one race scenario experienced by every candidate.
    """
    strategy_list = list(strategies)
    if not strategy_list:
        raise ValueError("at least one strategy is required")
    if runs <= 0:
        raise ValueError("runs must be positive")
    seeds = np.random.default_rng(seed).integers(0, 2**63, size=runs)
    results = [
        [simulate_race(race, strategy, int(run_seed)) for strategy in strategy_list]
        for run_seed in seeds
    ]
    times = np.array([[result.total_time for result in run] for run in results])
    winners = np.argmin(times, axis=1)
    win_counts = np.bincount(winners, minlength=len(strategy_list))
    evaluations = []
    for index, strategy in enumerate(strategy_list):
        values = times[:, index]
        summary = SimulationSummary(
            float(values.mean()),
            float(np.median(values)),
            float(values.std()),
            float(np.percentile(values, 10)),
            float(np.percentile(values, 90)),
            float(len(strategy.stops)),
            float(np.mean([not run[index].finished for run in results])),
        )
        evaluations.append(
            StrategyEvaluation(strategy, summary, float(win_counts[index] / runs))
        )
    return sorted(evaluations, key=lambda evaluation: evaluation.summary.mean)


def format_strategy(strategy: Strategy) -> str:
    """Return a compact command-line representation of a strategy."""
    return "-".join(
        [strategy.starting_compound]
        + [part for stop in strategy.stops for part in (str(stop.lap), stop.compound)]
    )
