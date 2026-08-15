"""Composable lap-time model."""

from race_strategy.models.race import RaceConfig
from race_strategy.models.tyre import TyreCompound

from .degradation import degradation_penalty, warmup_penalty


def calculate_lap_time(
    race: RaceConfig,
    tyre: TyreCompound,
    tyre_age: int,
    fuel: float,
    random_variation: float = 0.0,
    race_control_multiplier: float = 1.0,
) -> tuple[float, float, float, float]:
    """Calculate lap time and its degradation, warm-up, and fuel effects."""
    degradation = degradation_penalty(
        tyre, tyre_age, race.driver.tyre_management_factor
    )
    warmup = warmup_penalty(tyre, tyre_age)
    fuel_penalty = fuel * race.car.fuel_effect_per_kg
    lap_time = (
        race.baseline_lap_time
        + race.car.base_pace
        + race.driver.pace_delta
        + tyre.base_delta
        + degradation
        + warmup
        + fuel_penalty
        + random_variation
    ) * race_control_multiplier
    return lap_time, degradation, warmup, fuel_penalty
