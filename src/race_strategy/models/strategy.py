"""Models describing a driver's planned tyre strategy."""

from pydantic import BaseModel, Field


class PitStop(BaseModel):
    """A pit stop scheduled before a specified lap."""

    lap: int = Field(ge=1)
    compound: str = Field(min_length=1)


class Strategy(BaseModel):
    """Starting tyre compound and ordered pit-stop plan."""

    starting_compound: str = Field(min_length=1)
    stops: list[PitStop] = Field(default_factory=list)

    def model_post_init(self, __context: object) -> None:
        """Ensure pit stops occur at distinct laps in chronological order.

        Args:
            __context: Pydantic validation context, unused by this model.

        Raises:
            ValueError: If pit-stop laps are not strictly increasing.
        """
        laps = [stop.lap for stop in self.stops]
        if laps != sorted(laps) or len(laps) != len(set(laps)):
            raise ValueError("pit stops must have strictly increasing laps")
