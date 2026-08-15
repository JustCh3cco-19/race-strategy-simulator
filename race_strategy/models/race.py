"""Models for complete race configuration and strategy validation."""

from pydantic import BaseModel, Field

from .car import Car
from .circuit import Circuit
from .driver import Driver
from .race_control import RaceControlEvent, RaceControlRandomization
from .strategy import Strategy
from .tyre import TyreCompound


class RaceConfig(BaseModel):
    """Validated inputs required to simulate one race."""

    name: str = Field(min_length=1)
    laps: int = Field(gt=0)
    baseline_lap_time: float = Field(gt=0)
    circuit: Circuit
    car: Car
    driver: Driver
    tyres: dict[str, TyreCompound] = Field(min_length=1)
    race_control: list[RaceControlEvent] = Field(default_factory=list)
    race_control_random: RaceControlRandomization = Field(
        default_factory=RaceControlRandomization
    )

    def model_post_init(self, __context: object) -> None:
        """Ensure configured race-control intervals fit within the race."""
        invalid_events = [
            event
            for event in self.race_control
            if event.start_lap > self.laps or event.end_lap > self.laps
        ]
        if invalid_events:
            raise ValueError("race-control events must fit within the race laps")
        if self.race_control_random.duration > self.laps:
            raise ValueError("random race-control duration must fit within the race")

    def validate_strategy(self, strategy: Strategy) -> None:
        """Validate tyre choices and pit-stop timing for this race.

        Args:
            strategy: Strategy to validate against the configured race.

        Raises:
            ValueError: If a compound is unknown or a stop is on the final lap.
        """
        compounds = {name.lower() for name in self.tyres}
        requested = [strategy.starting_compound, *(s.compound for s in strategy.stops)]
        missing = [name for name in requested if name.lower() not in compounds]
        if missing:
            raise ValueError(f"unknown tyre compound(s): {', '.join(missing)}")
        if any(stop.lap <= 1 for stop in strategy.stops):
            raise ValueError("pit stops must occur after the first lap")
        if any(stop.lap >= self.laps for stop in strategy.stops):
            raise ValueError("pit stops must occur before the final lap")
        compounds_by_stint = [
            strategy.starting_compound.lower(),
            *(stop.compound.lower() for stop in strategy.stops),
        ]
        boundaries = (0, *(stop.lap for stop in strategy.stops), self.laps)
        for compound, start, end in zip(compounds_by_stint, boundaries, boundaries[1:]):
            tyre = next(
                value for name, value in self.tyres.items() if name.lower() == compound
            )
            stint_length = end - start
            if stint_length < tyre.minimum_stint:
                raise ValueError(
                    f"{compound} stint is shorter than minimum_stint "
                    f"({tyre.minimum_stint})"
                )
            if tyre.maximum_stint is not None and stint_length > tyre.maximum_stint:
                raise ValueError(
                    f"{compound} stint exceeds maximum_stint ({tyre.maximum_stint})"
                )
