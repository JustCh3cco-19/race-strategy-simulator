"""Pydantic model for tyre compound performance parameters."""

from pydantic import BaseModel, Field


class TyreCompound(BaseModel):
    """Degradation, warm-up, and stint constraints for one compound."""

    name: str = Field(min_length=1)
    base_delta: float
    degradation_rate: float = Field(ge=0)
    warmup_penalty: float = Field(default=0, ge=0)
    warmup_laps: int = Field(default=0, ge=0)
    cliff_lap: int | None = Field(default=None, ge=1)
    cliff_penalty: float = Field(default=0, ge=0)
    minimum_stint: int = Field(default=1, ge=1)
    maximum_stint: int | None = Field(default=None, ge=1)

    def model_post_init(self, __context: object) -> None:
        """Ensure the optional maximum stint is not shorter than the minimum.

        Args:
            __context: Pydantic validation context, unused by this model.

        Raises:
            ValueError: If ``maximum_stint`` is below ``minimum_stint``.
        """
        if self.maximum_stint is not None and self.maximum_stint < self.minimum_stint:
            raise ValueError("maximum_stint must be >= minimum_stint")
