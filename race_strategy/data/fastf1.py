"""FastF1 adapter with an explicit offline cache boundary."""

from math import isfinite
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class SessionLap(BaseModel):
    """Normalized observed lap data independent of FastF1 internals."""

    driver: str = Field(min_length=1)
    lap: int = Field(ge=1)
    lap_time: float = Field(gt=0)
    stint: int = Field(ge=1)
    compound: str = Field(min_length=1)
    tyre_age: int = Field(ge=1)


def load_offline_laps(path: Path) -> list[SessionLap]:
    """Load normalized laps from a YAML fixture."""
    with path.open(encoding="utf-8") as file:
        raw = yaml.safe_load(file)
    if not isinstance(raw, list):
        raise ValueError("lap fixture root must be a list")
    return [SessionLap.model_validate(item) for item in raw]


def save_offline_laps(path: Path, laps: list[SessionLap]) -> None:
    """Save normalized laps as a reproducible YAML fixture.

    Args:
        path: Destination YAML path.
        laps: Normalized session laps to serialize.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(
            [lap.model_dump(mode="json") for lap in laps],
            file,
            sort_keys=False,
        )


def load_fastf1_laps(
    year: int, event: str, session: str, cache_dir: Path
) -> list[SessionLap]:
    """Load and normalize a FastF1 session, using its cache directory.

    FastF1 is imported at call time so offline fixture loading remains usable
    when a caller does not need to access a remote session.
    """
    try:
        import fastf1  # type: ignore[import-untyped]
    except ImportError as error:
        raise RuntimeError("FastF1 is required to load remote sessions") from error
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))
    try:
        session_data = fastf1.get_session(year, event, session)
        session_data.load(telemetry=False, weather=False, messages=False)
    except Exception as error:
        raise RuntimeError(
            f"unable to load FastF1 session {year} {event} {session}; "
            "check network access or use a cached/offline fixture"
        ) from error
    laps = session_data.laps
    normalized: list[SessionLap] = []
    for row in laps.itertuples():
        if (
            row.LapTime is None
            or row.Driver is None
            or row.Compound is None
            or row.Stint is None
            or row.TyreLife is None
        ):
            continue
        lap_number = row.LapNumber
        lap_seconds = row.LapTime.total_seconds()
        if (
            lap_number is None
            or row.Driver == ""
            or not isfinite(float(lap_number))
            or not isfinite(float(lap_seconds))
            or not isfinite(float(row.Stint))
            or not isfinite(float(row.TyreLife))
        ):
            continue
        normalized.append(
            SessionLap(
                driver=row.Driver,
                lap=int(lap_number),
                lap_time=float(lap_seconds),
                stint=int(row.Stint),
                compound=str(row.Compound),
                tyre_age=int(row.TyreLife),
            )
        )
    return normalized
