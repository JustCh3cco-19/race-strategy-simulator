"""Command-line interface for validating race configurations."""

from pathlib import Path

import typer

from .config import load_race_config

app = typer.Typer(help="Motorsport race strategy simulator.")


@app.command()
def validate(config: Path = typer.Option(..., exists=True, readable=True)) -> None:
    """Validate a race YAML configuration.

    Args:
        config: Path to the YAML configuration file.
    """
    race = load_race_config(config)
    typer.echo(f"Valid configuration: {race.name} ({race.laps} laps)")


if __name__ == "__main__":
    app()
