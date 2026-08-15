"""Tests for interactive replay reports."""

from pathlib import Path

from race_strategy.analytics.plots import write_race_plot
from race_strategy.config import load_race_config
from race_strategy.models.strategy import Strategy
from race_strategy.simulation.engine import simulate_race


def test_race_plot_is_written(tmp_path: Path) -> None:
    """Write a self-contained HTML report for a simulated race."""
    race = load_race_config(Path("configs/example_race.yaml"))
    result = simulate_race(race, Strategy(starting_compound="medium"), seed=2)
    output = tmp_path / "replay.html"

    write_race_plot(result, output)

    assert output.exists()
    assert "plotly" in output.read_text(encoding="utf-8").lower()
