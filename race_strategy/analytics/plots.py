"""Interactive Plotly reports for race replays."""

from pathlib import Path

import plotly.graph_objects as go  # type: ignore[import-untyped]
from plotly.subplots import make_subplots  # type: ignore[import-untyped]

from race_strategy.models.result import RaceResult


def write_race_plot(result: RaceResult, path: Path) -> None:
    """Write an interactive HTML plot for a race replay.

    Args:
        result: Completed or retired race result.
        path: Destination HTML file.
    """
    laps = result.laps
    figure = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("Lap time", "Fuel and tyre age", "Lap penalties"),
    )
    numbers = [lap.lap for lap in laps]
    figure.add_trace(
        go.Scatter(x=numbers, y=[lap.lap_time for lap in laps], name="Lap time"),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Scatter(x=numbers, y=[lap.fuel for lap in laps], name="Fuel"),
        row=2,
        col=1,
    )
    figure.add_trace(
        go.Scatter(x=numbers, y=[lap.tyre_age for lap in laps], name="Tyre age"),
        row=2,
        col=1,
    )
    figure.add_trace(
        go.Bar(
            x=numbers,
            y=[
                lap.degradation_penalty
                + lap.warmup_penalty
                + lap.traffic_penalty
                + lap.pit_stop_loss
                for lap in laps
            ],
            name="Penalties",
        ),
        row=3,
        col=1,
    )
    figure.update_xaxes(title_text="Lap", row=3, col=1)
    figure.update_yaxes(title_text="Seconds", row=1, col=1)
    figure.update_yaxes(title_text="Fuel / laps", row=2, col=1)
    figure.update_yaxes(title_text="Seconds", row=3, col=1)
    figure.update_layout(title="Race strategy replay", height=900)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(str(path), include_plotlyjs=True)
