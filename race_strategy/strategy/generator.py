"""Generation of legal pit-stop strategies."""

from collections.abc import Iterator
from itertools import combinations, product

from race_strategy.models.race import RaceConfig
from race_strategy.models.strategy import PitStop, Strategy


def generate_strategies(
    race: RaceConfig,
    min_stops: int = 0,
    max_stops: int = 2,
    pit_window: int = 1,
) -> Iterator[Strategy]:
    """Yield legal strategies for a race configuration.

    Args:
        race: Configuration defining compounds and race length.
        min_stops: Inclusive lower bound for pit stops.
        max_stops: Inclusive upper bound for pit stops.
        pit_window: Spacing between candidate pit-stop laps. A value of five
            considers laps 5, 10, 15, and so on, reducing search size.

    Yields:
        Strategies satisfying each selected compound's stint constraints.

    Raises:
        ValueError: If the generator bounds are invalid.
    """
    if min_stops < 0 or max_stops < min_stops:
        raise ValueError("stop bounds must satisfy 0 <= min_stops <= max_stops")
    if pit_window < 1:
        raise ValueError("pit_window must be positive")
    compounds = tuple(name.lower() for name in race.tyres)
    # Lap one is excluded because the simulator requires a non-empty opening
    # stint before the first compound change.
    first_candidate_lap = max(2, pit_window)
    candidate_laps = range(first_candidate_lap, race.laps, pit_window)
    for stop_count in range(min_stops, max_stops + 1):
        for stop_laps in combinations(candidate_laps, stop_count):
            stint_lengths = tuple(
                end - start
                for start, end in zip((0, *stop_laps), (*stop_laps, race.laps))
            )
            for selected in product(compounds, repeat=stop_count + 1):
                if not _stints_are_legal(race, selected, stint_lengths):
                    continue
                yield Strategy(
                    starting_compound=selected[0],
                    stops=[
                        PitStop(lap=lap, compound=compound)
                        for lap, compound in zip(stop_laps, selected[1:])
                    ],
                )


def _stints_are_legal(
    race: RaceConfig, compounds: tuple[str, ...], lengths: tuple[int, ...]
) -> bool:
    """Return whether every stint satisfies its compound constraints."""
    for compound, length in zip(compounds, lengths):
        tyre = next(
            value for name, value in race.tyres.items() if name.lower() == compound
        )
        if length < tyre.minimum_stint:
            return False
        if tyre.maximum_stint is not None and length > tyre.maximum_stint:
            return False
    return True
