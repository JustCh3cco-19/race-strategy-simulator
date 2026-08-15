"""Tests for normalized FastF1 data and offline fixture handling."""

import sys
from datetime import timedelta
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from pydantic import ValidationError

from race_strategy.config import load_race_config, save_race_config
from race_strategy.data.calibration import apply_calibration, calibrate_laps
from race_strategy.data.fastf1 import (
    SessionLap,
    load_fastf1_laps,
    load_offline_laps,
    save_offline_laps,
)


def test_offline_fixture_loads() -> None:
    """Load the bundled fixture into normalized session-lap models."""
    laps = load_offline_laps(Path("configs/example_session_laps.yaml"))

    assert len(laps) == 3
    assert laps[0].driver == "VER"
    assert laps[-1].tyre_age == 3


def test_offline_fixture_round_trip(tmp_path: Path) -> None:
    """Serialize normalized laps and load them without changing values."""
    source = load_offline_laps(Path("configs/example_session_laps.yaml"))
    destination = tmp_path / "laps.yaml"

    save_offline_laps(destination, source)

    assert load_offline_laps(destination) == source


def test_session_lap_rejects_non_finite_lap_time() -> None:
    """Reject non-finite lap times before they enter the simulator."""
    with pytest.raises(ValidationError):
        SessionLap(
            driver="VER",
            lap=1,
            lap_time=float("nan"),
            stint=1,
            compound="MEDIUM",
            tyre_age=1,
        )


def test_fastf1_adapter_normalizes_valid_rows(monkeypatch, tmp_path: Path) -> None:
    """Normalize valid FastF1 rows while skipping incomplete rows."""
    valid_row = SimpleNamespace(
        LapTime=timedelta(seconds=92.4),
        Driver="VER",
        Compound="MEDIUM",
        Stint=1,
        TyreLife=2,
        LapNumber=3,
    )
    incomplete_row = SimpleNamespace(
        LapTime=None,
        Driver="VER",
        Compound="MEDIUM",
        Stint=1,
        TyreLife=2,
        LapNumber=4,
    )
    fake_session = SimpleNamespace(
        laps=SimpleNamespace(itertuples=lambda: iter([valid_row, incomplete_row])),
        load=lambda **_: None,
    )
    fake_fastf1 = ModuleType("fastf1")
    fake_fastf1.Cache = SimpleNamespace(enable_cache=lambda _: None)
    fake_fastf1.get_session = lambda *_: fake_session
    monkeypatch.setitem(sys.modules, "fastf1", fake_fastf1)

    laps = load_fastf1_laps(2024, "Monza", "R", tmp_path)

    assert laps == [
        SessionLap(
            driver="VER",
            lap=3,
            lap_time=92.4,
            stint=1,
            compound="MEDIUM",
            tyre_age=2,
        )
    ]


def test_calibration_estimates_degradation() -> None:
    """Fit a positive degradation slope from the bundled fixture."""
    laps = load_offline_laps(Path("configs/example_session_laps.yaml"))

    calibration = calibrate_laps(laps)["MEDIUM"]

    assert calibration.base_lap_time == pytest.approx(92.35)
    assert calibration.degradation_rate == pytest.approx(0.05)
    assert calibration.sample_count == 3


def test_calibration_rejects_empty_data() -> None:
    """Reject calibration when no observed laps are available."""
    with pytest.raises(ValueError, match="at least one lap"):
        calibrate_laps([])


def test_calibration_updates_race_config(tmp_path: Path) -> None:
    """Apply fitted parameters and preserve the YAML configuration shape."""
    config = load_race_config(Path("configs/example_race.yaml"))
    laps = load_offline_laps(Path("configs/example_session_laps.yaml"))
    calibrated = apply_calibration(config, calibrate_laps(laps))
    destination = tmp_path / "calibrated.yaml"

    save_race_config(destination, calibrated)

    loaded = load_race_config(destination)
    assert loaded.tyres["medium"].degradation_rate == pytest.approx(0.05)
    assert loaded.tyres["medium"].base_delta == pytest.approx(2.35)
