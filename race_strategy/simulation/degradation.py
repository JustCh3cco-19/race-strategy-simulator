"""Tyre degradation calculations."""

from race_strategy.models.tyre import TyreCompound


def degradation_penalty(
    tyre: TyreCompound, tyre_age: int, management_factor: float = 1.0
) -> float:
    """Return degradation, including the optional tyre cliff."""
    penalty = tyre.degradation_rate * tyre_age * management_factor
    if tyre.cliff_lap is not None and tyre_age >= tyre.cliff_lap:
        penalty += tyre.cliff_penalty
    return penalty


def warmup_penalty(tyre: TyreCompound, tyre_age: int) -> float:
    """Return the warm-up penalty while a tyre is below its warm-up age."""
    return tyre.warmup_penalty if tyre_age <= tyre.warmup_laps else 0.0
