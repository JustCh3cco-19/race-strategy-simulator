"""Models for complete race configuration and strategy validation."""

from pydantic import BaseModel, Field

from .car import Car
from .circuit import Circuit
from .driver import Driver
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
        if any(stop.lap >= self.laps for stop in strategy.stops):
            raise ValueError("pit stops must occur before the final lap")
