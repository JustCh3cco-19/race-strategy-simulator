"""Statistical metrics for collections of race results."""

from dataclasses import dataclass

import numpy as np

from race_strategy.models.result import RaceResult


@dataclass(frozen=True)
class RaceMetrics:
    """Aggregate metrics calculated from simulated race results."""

    mean: float
    median: float
    standard_deviation: float
    p10: float
    p90: float
    average_pit_stops: float
    retirement_rate: float


def summarize_results(results: list[RaceResult]) -> RaceMetrics:
    """Summarize race times, pit stops, and retirements.

    Args:
        results: Non-empty collection of completed or retired race results.

    Returns:
        Aggregate time and reliability metrics.

    Raises:
        ValueError: If ``results`` is empty.
    """
    if not results:
        raise ValueError("at least one race result is required")
    times = np.array([result.total_time for result in results])
    return RaceMetrics(
        mean=float(times.mean()),
        median=float(np.median(times)),
        standard_deviation=float(times.std()),
        p10=float(np.percentile(times, 10)),
        p90=float(np.percentile(times, 90)),
        average_pit_stops=float(np.mean([result.pit_stops for result in results])),
        retirement_rate=float(np.mean([not result.finished for result in results])),
    )
