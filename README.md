# Race Strategy Simulator

A configurable and testable motorsport race strategy simulator. The project is in its foundation phase: this first version validates YAML configurations and strategies.

## Installation

```bash
git clone <repository>
cd race-strategy-simulator
uv sync
```

## Usage

```bash
uv run race-strategy --help
uv run race-strategy validate --config configs/example_race.yaml
```

## Development

```bash
uv run pytest
uv run ruff check .
uv run mypy race_strategy
```

The roadmap and architectural decisions are documented in `docs/project-spec.md` and `docs/architecture.md`.
