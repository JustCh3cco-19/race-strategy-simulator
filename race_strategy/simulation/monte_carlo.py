"""Monte Carlo strategy evaluation."""

from dataclasses import asdict, dataclass

import numpy as np

from race_strategy.analytics.metrics import summarize_results
from race_strategy.models.race import RaceConfig
from race_strategy.models.strategy import Strategy

from .engine import simulate_race


@dataclass(frozen=True)
class SimulationSummary:
    """Summary statistics for repeated strategy simulations."""

    mean: float
    median: float
    standard_deviation: float
    p10: float
    p90: float
    average_pit_stops: float = 0.0
    retirement_rate: float = 0.0


def monte_carlo(
    race: RaceConfig, strategy: Strategy, runs: int, seed: int = 0
) -> SimulationSummary:
    """Evaluate a strategy repeatedly with reproducible independent seeds."""
    if runs <= 0:
        raise ValueError("runs must be positive")
    seeds = np.random.default_rng(seed).integers(0, 2**63, size=runs)
    results = [simulate_race(race, strategy, int(value)) for value in seeds]
    return SimulationSummary(**asdict(summarize_results(results)))
