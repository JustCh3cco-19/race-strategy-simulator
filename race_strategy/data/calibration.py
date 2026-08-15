"""Calibration of simple lap-time parameters from observed session laps."""

from collections import defaultdict
from dataclasses import asdict, dataclass

import numpy as np
import yaml

from race_strategy.models.race import RaceConfig

from .fastf1 import SessionLap


@dataclass(frozen=True)
class CompoundCalibration:
    """Fitted linear lap-time parameters for one tyre compound."""

    compound: str
    base_lap_time: float
    degradation_rate: float
    sample_count: int
    residual_rmse: float


def calibrate_laps(laps: list[SessionLap]) -> dict[str, CompoundCalibration]:
    """Fit lap time as ``base_lap_time + degradation_rate * tyre_age``.

    Args:
        laps: Normalized observed laps. Laps are grouped case-insensitively by
            compound before fitting.

    Returns:
        Calibration parameters keyed by normalized upper-case compound name.

    Raises:
        ValueError: If no laps are supplied.
    """
    if not laps:
        raise ValueError("at least one lap is required for calibration")
    grouped: defaultdict[str, list[SessionLap]] = defaultdict(list)
    for lap in laps:
        grouped[lap.compound.upper()].append(lap)

    calibrations: dict[str, CompoundCalibration] = {}
    for compound, observations in grouped.items():
        ages = np.array([lap.tyre_age for lap in observations], dtype=float)
        times = np.array([lap.lap_time for lap in observations], dtype=float)
        if len(observations) >= 2 and np.ptp(ages) > 0:
            slope, intercept = np.polyfit(ages, times, 1)
        else:
            slope = 0.0
            intercept = float(times.mean())
        predicted = intercept + slope * ages
        calibrations[compound] = CompoundCalibration(
            compound=compound,
            base_lap_time=float(intercept),
            degradation_rate=max(0.0, float(slope)),
            sample_count=len(observations),
            residual_rmse=float(np.sqrt(np.mean((times - predicted) ** 2))),
        )
    return calibrations


def save_calibration(path: str, calibration: dict[str, CompoundCalibration]) -> None:
    """Save calibration parameters to a YAML file."""
    with open(path, "w", encoding="utf-8") as file:
        yaml.safe_dump(
            {name: asdict(value) for name, value in calibration.items()},
            file,
            sort_keys=False,
        )


def apply_calibration(
    race: RaceConfig, calibration: dict[str, CompoundCalibration]
) -> RaceConfig:
    """Apply fitted compound parameters to a race configuration.

    The fitted intercept is converted to ``base_delta`` relative to the race
    baseline, while the fitted slope replaces the configured degradation rate.
    Compounds without observations retain their original parameters.

    Args:
        race: Configuration to copy and calibrate.
        calibration: Parameters keyed by upper-case compound name.

    Returns:
        A new calibrated configuration. The input object is not modified.
    """
    tyres = {}
    for key, tyre in race.tyres.items():
        fitted = calibration.get(key.upper())
        if fitted is None:
            tyres[key] = tyre
            continue
        tyres[key] = tyre.model_copy(
            update={
                "base_delta": fitted.base_lap_time - race.baseline_lap_time,
                "degradation_rate": fitted.degradation_rate,
            }
        )
    return race.model_copy(update={"tyres": tyres})
