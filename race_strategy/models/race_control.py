"""Configurable race-control events."""

from enum import StrEnum

from pydantic import BaseModel, Field


class RaceControlState(StrEnum):
    """Track state used by the lap and pit-stop models."""

    GREEN = "GREEN"
    VSC = "VSC"
    SAFETY_CAR = "SAFETY_CAR"


class RaceControlEvent(BaseModel):
    """Race-control state active for an inclusive lap interval."""

    state: RaceControlState
    start_lap: int = Field(ge=1)
    end_lap: int = Field(ge=1)

    def model_post_init(self, __context: object) -> None:
        """Ensure the event interval is ordered."""
        if self.end_lap < self.start_lap:
            raise ValueError("race-control end_lap must be >= start_lap")

    def applies_to(self, lap: int) -> bool:
        """Return whether this event is active on ``lap``."""
        return self.start_lap <= lap <= self.end_lap


class RaceControlRandomization(BaseModel):
    """Probabilities and duration for one random race-control event."""

    vsc_probability: float = Field(default=0, ge=0, le=1)
    safety_car_probability: float = Field(default=0, ge=0, le=1)
    duration: int = Field(default=2, ge=1)

    def model_post_init(self, __context: object) -> None:
        """Ensure event probabilities form a valid mutually exclusive draw."""
        if self.vsc_probability + self.safety_car_probability > 1:
            raise ValueError("race-control probabilities must sum to <= 1")
