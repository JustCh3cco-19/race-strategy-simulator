"""Tests for YAML race-configuration loading."""

from pathlib import Path

import pytest

from race_strategy.config import load_race_config
from race_strategy.models.race import RaceConfig
from race_strategy.models.race_control import RaceControlEvent


def test_example_configuration_loads() -> None:
    """Verify that the bundled example configuration is parsed correctly."""
    config = load_race_config(Path("configs/example_race.yaml"))
    # These assertions cover both a race-level field and nested tyre data.
    assert config.laps == 58
    assert config.tyres["medium"].degradation_rate == 0.045


def test_race_control_event_must_fit_race() -> None:
    """Reject an event extending beyond the configured race distance."""
    config = load_race_config(Path("configs/example_race.yaml"))

    with pytest.raises(ValueError, match="must fit"):
        RaceConfig.model_validate(
            {
                **config.model_dump(),
                "race_control": [
                    RaceControlEvent(state="VSC", start_lap=58, end_lap=59)
                ],
            }
        )
