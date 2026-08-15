"""Utilities for loading validated race configurations from YAML files."""

from pathlib import Path
from typing import Any

import yaml

from .models.race import RaceConfig


def load_race_config(path: Path) -> RaceConfig:
    """Load and validate a race configuration from a YAML file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        A validated :class:`RaceConfig` instance.

    Raises:
        ValueError: If the YAML root is not a mapping.
        pydantic.ValidationError: If the configuration fails model validation.
    """
    with path.open(encoding="utf-8") as file:
        raw: Any = yaml.safe_load(file)
    if not isinstance(raw, dict):
        raise ValueError("configuration root must be a mapping")
    race = raw.get("race", {})
    circuit = raw.get("circuit", {})
    # Flatten the YAML sections because RaceConfig expects nested model values
    # alongside the race-level fields.
    payload = {
        **race,
        "circuit": circuit,
        "car": raw.get("car", {}),
        "driver": raw.get("driver", {}),
        "tyres": raw.get("tyres", {}),
        "race_control": raw.get("race_control", []),
        "race_control_random": raw.get("race_control_random", {}),
    }
    return RaceConfig.model_validate(payload)


def save_race_config(path: Path, race: RaceConfig) -> None:
    """Save a validated race configuration in the project's YAML format."""
    payload = {
        "race": {
            "name": race.name,
            "laps": race.laps,
            "baseline_lap_time": race.baseline_lap_time,
        },
        "circuit": race.circuit.model_dump(mode="json"),
        "car": race.car.model_dump(mode="json"),
        "driver": race.driver.model_dump(mode="json"),
        "tyres": {
            name: tyre.model_dump(mode="json") for name, tyre in race.tyres.items()
        },
        "race_control": [event.model_dump(mode="json") for event in race.race_control],
        "race_control_random": race.race_control_random.model_dump(mode="json"),
    }
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(payload, file, sort_keys=False)
