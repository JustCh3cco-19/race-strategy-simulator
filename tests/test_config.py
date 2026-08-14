"""Tests for YAML race-configuration loading."""

from pathlib import Path

from race_strategy.config import load_race_config


def test_example_configuration_loads() -> None:
    """Verify that the bundled example configuration is parsed correctly."""
    config = load_race_config(Path("configs/example_race.yaml"))
    assert config.laps == 58
    assert config.tyres["medium"].degradation_rate == 0.045
