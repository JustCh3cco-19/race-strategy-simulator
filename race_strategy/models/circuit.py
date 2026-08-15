"""Pydantic model describing circuit-specific race parameters."""

from pydantic import BaseModel, Field


class Circuit(BaseModel):
    """Track characteristics used by the race simulation."""

    name: str = Field(min_length=1)
    pit_lane_loss: float = Field(gt=0)
    safety_car_lap_time_multiplier: float = Field(default=1.25, gt=0)
    vsc_lap_time_multiplier: float = Field(default=1.10, gt=0)
    overtaking_difficulty: float = Field(default=0.5, ge=0, le=1)
    traffic_probability: float = Field(default=0.0, ge=0, le=1)
    traffic_penalty: float = Field(default=0.0, ge=0)
