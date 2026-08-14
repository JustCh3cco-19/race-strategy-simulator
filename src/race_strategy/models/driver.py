"""Pydantic model describing a driver's performance characteristics."""

from pydantic import BaseModel, Field


class Driver(BaseModel):
    """Pace, consistency, and tyre-management parameters for a driver."""

    name: str = Field(min_length=1)
    pace_delta: float = 0
    lap_time_variance: float = Field(default=0, ge=0)
    tyre_management_factor: float = Field(default=1, gt=0)
    consistency: float = Field(default=1, ge=0, le=1)
