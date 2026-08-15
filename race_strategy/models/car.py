"""Pydantic model describing the simulated car's properties."""

from pydantic import BaseModel, Field


class Car(BaseModel):
    """Physical and reliability parameters for a race car."""

    base_pace: float = 0
    fuel_effect_per_kg: float = Field(ge=0)
    initial_fuel: float = Field(gt=0)
    fuel_consumption_per_lap: float = Field(gt=0)
    pit_stop_variance: float = Field(default=0, ge=0)
    reliability: float = Field(default=1, ge=0, le=1)
    retirement_penalty: float = Field(default=300, ge=0)
