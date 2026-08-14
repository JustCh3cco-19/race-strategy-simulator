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
    }
    return RaceConfig.model_validate(payload)
