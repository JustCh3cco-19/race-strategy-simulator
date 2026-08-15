"""Pit-stop time calculations."""


def pit_stop_loss(
    pit_lane_loss: float,
    stationary_time: float = 2.5,
    variance: float = 0.0,
    race_control_multiplier: float = 1.0,
) -> float:
    """Return effective pit-stop loss, including stationary time and noise."""
    return max(
        0.0, (pit_lane_loss + stationary_time + variance) * race_control_multiplier
    )
