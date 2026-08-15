"""Serializable result models produced by the race simulator."""

from pydantic import BaseModel, Field

from .strategy import Strategy


class LapResult(BaseModel):
    """Simulation output for one completed lap."""

    lap: int = Field(ge=1)
    lap_time: float = Field(gt=0)
    tyre: str = Field(min_length=1)
    tyre_age: int = Field(ge=1)
    fuel: float = Field(ge=0)
    degradation_penalty: float = Field(ge=0)
    warmup_penalty: float = Field(ge=0)
    fuel_penalty: float = Field(ge=0)
    traffic_penalty: float = Field(default=0, ge=0)
    pit_stop_loss: float = Field(default=0, ge=0)
    race_control: str = "GREEN"


class StintResult(BaseModel):
    """Summary of one tyre stint."""

    compound: str = Field(min_length=1)
    start_lap: int = Field(ge=1)
    end_lap: int = Field(ge=1)


class RaceResult(BaseModel):
    """Complete result of one simulated race."""

    total_time: float = Field(gt=0)
    strategy: Strategy
    laps: list[LapResult]
    stints: list[StintResult]
    pit_stops: int = Field(ge=0)
    finished: bool = True
    failure_lap: int | None = Field(default=None, ge=1)
    warnings: list[str] = Field(default_factory=list)
