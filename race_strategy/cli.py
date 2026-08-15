"""Command-line interface for validating race configurations."""

from itertools import islice
from pathlib import Path

import typer

from .analytics.plots import write_race_plot
from .config import load_race_config, save_race_config
from .data.calibration import apply_calibration, calibrate_laps, save_calibration
from .data.fastf1 import load_fastf1_laps, load_offline_laps, save_offline_laps
from .models.strategy import PitStop, Strategy
from .simulation.engine import simulate_race
from .strategy.evaluator import (
    format_strategy,
    rank_strategies_common_random_numbers,
)
from .strategy.generator import generate_strategies

app = typer.Typer(help="Motorsport race strategy simulator.")


@app.command()
def validate(config: Path = typer.Option(..., exists=True, readable=True)) -> None:
    """Validate a race YAML configuration.

    Args:
        config: Path to the YAML configuration file.
    """
    race = load_race_config(config)
    typer.echo(f"Valid configuration: {race.name} ({race.laps} laps)")


@app.command("fetch-data")
def fetch_data(
    year: int = typer.Option(..., min=1950),
    event: str = typer.Option(..., help="FastF1 event name or official identifier."),
    session: str = typer.Option("R", help="FastF1 session identifier."),
    cache_dir: Path = typer.Option(Path(".cache/fastf1")),
    output: Path = typer.Option(..., help="YAML path for normalized lap data."),
    fixture: Path | None = typer.Option(
        None, help="Load an existing normalized fixture instead of FastF1."
    ),
) -> None:
    """Fetch or copy normalized session laps into an offline YAML fixture."""
    laps = (
        load_offline_laps(fixture)
        if fixture is not None
        else load_fastf1_laps(year, event, session, cache_dir)
    )
    save_offline_laps(output, laps)
    typer.echo(f"Saved {len(laps)} normalized laps to {output}")


@app.command("calibrate-data")
def calibrate_data(
    input_path: Path = typer.Option(..., exists=True, readable=True),
    output: Path = typer.Option(..., help="YAML path for fitted parameters."),
) -> None:
    """Fit tyre degradation parameters from normalized session laps."""
    calibration = calibrate_laps(load_offline_laps(input_path))
    save_calibration(str(output), calibration)
    typer.echo(f"Saved calibration for {len(calibration)} compounds to {output}")


@app.command("calibrate-config")
def calibrate_config(
    config: Path = typer.Option(..., exists=True, readable=True),
    input_path: Path = typer.Option(..., exists=True, readable=True),
    output: Path = typer.Option(..., help="YAML path for the calibrated race."),
) -> None:
    """Apply observed lap calibration directly to a race configuration."""
    race = load_race_config(config)
    laps = load_offline_laps(input_path)
    calibrated = apply_calibration(race, calibrate_laps(laps))
    output.parent.mkdir(parents=True, exist_ok=True)
    save_race_config(output, calibrated)
    typer.echo(f"Saved calibrated race configuration to {output}")


def _parse_strategy(value: str) -> Strategy:
    """Parse a compact strategy such as ``medium-30-hard``."""
    parts = [part.strip().lower() for part in value.split("-") if part.strip()]
    if not parts:
        raise typer.BadParameter("strategy cannot be empty")
    if len(parts) == 1:
        return Strategy(starting_compound=parts[0])
    if len(parts) % 2 == 0:
        raise typer.BadParameter("stops must be expressed as compound-lap pairs")
    stops = [
        PitStop(lap=int(parts[index]), compound=parts[index + 1])
        for index in range(1, len(parts), 2)
    ]
    return Strategy(starting_compound=parts[0], stops=stops)


@app.command()
def simulate(
    config: Path = typer.Option(..., exists=True, readable=True),
    strategy: str = typer.Option(..., help="Example: medium-30-hard"),
    seed: int = typer.Option(0),
    output: Path | None = typer.Option(
        None, help="Optional JSON path for the complete race replay."
    ),
    plot: Path | None = typer.Option(
        None, help="Optional HTML path for an interactive Plotly replay."
    ),
) -> None:
    """Simulate one race and optionally save its complete replay as JSON."""
    result = simulate_race(load_race_config(config), _parse_strategy(strategy), seed)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        typer.echo(f"Saved race replay to {output}")
    if plot is not None:
        write_race_plot(result, plot)
        typer.echo(f"Saved interactive race plot to {plot}")
    typer.echo(f"Total time: {result.total_time:.3f} s ({result.pit_stops} stops)")


@app.command()
def compare(
    config: Path = typer.Option(..., exists=True, readable=True),
    strategy: list[str] = typer.Option(..., help="Repeat for each strategy"),
    runs: int = typer.Option(100),
    seed: int = typer.Option(0),
) -> None:
    """Compare strategies using shared seeded Monte Carlo scenarios."""
    race = load_race_config(config)
    ranked = rank_strategies_common_random_numbers(
        race, (_parse_strategy(value) for value in strategy), runs, seed
    )
    for evaluation in ranked:
        value = format_strategy(evaluation.strategy)
        summary = evaluation.summary
        typer.echo(
            f"{value}: mean={summary.mean:.3f}s median={summary.median:.3f}s "
            f"std={summary.standard_deviation:.3f}s p10={summary.p10:.3f}s "
            f"p90={summary.p90:.3f}s stops={summary.average_pit_stops:.1f} "
            f"dnf={summary.retirement_rate:.1%} "
            f"fastest={evaluation.probability_fastest:.1%}"
        )


@app.command("generate-strategies")
def generate_strategies_command(
    config: Path = typer.Option(..., exists=True, readable=True),
    min_stops: int = typer.Option(0, min=0),
    max_stops: int = typer.Option(2, min=0),
    pit_window: int = typer.Option(5, min=1),
    limit: int = typer.Option(20, min=1),
) -> None:
    """Generate and print legal strategies up to a display limit."""
    race = load_race_config(config)
    count = 0
    for strategy in generate_strategies(race, min_stops, max_stops, pit_window):
        typer.echo(format_strategy(strategy))
        count += 1
        if count >= limit:
            break
    typer.echo(f"Generated {count} displayed strategy/strategies")


@app.command()
def optimize(
    config: Path = typer.Option(..., exists=True, readable=True),
    min_stops: int = typer.Option(0, min=0),
    max_stops: int = typer.Option(2, min=0),
    pit_window: int = typer.Option(5, min=1),
    strategies: int = typer.Option(100, min=1),
    runs: int = typer.Option(100, min=1),
    seed: int = typer.Option(0),
) -> None:
    """Find the fastest generated strategy by mean simulated time."""
    race = load_race_config(config)
    candidates = generate_strategies(race, min_stops, max_stops, pit_window)
    ranked = rank_strategies_common_random_numbers(
        race, islice(candidates, strategies), runs, seed
    )
    for rank, evaluation in enumerate(ranked[:10], start=1):
        summary = evaluation.summary
        typer.echo(
            f"{rank}. {format_strategy(evaluation.strategy)} "
            f"mean={summary.mean:.3f}s median={summary.median:.3f}s "
            f"std={summary.standard_deviation:.3f}s p10={summary.p10:.3f}s "
            f"p90={summary.p90:.3f}s stops={summary.average_pit_stops:.1f} "
            f"dnf={summary.retirement_rate:.1%} "
            f"fastest={evaluation.probability_fastest:.1%}"
        )


if __name__ == "__main__":
    app()
