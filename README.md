# Race Strategy Simulator

Race Strategy Simulator is a configurable, reproducible motorsport strategy
simulator. It uses FastF1 session data to build normalized inputs, models a
single car lap by lap, and compares tyre strategies with seeded Monte Carlo
runs.

The current implementation focuses on the single-car simulation workflow:

- tyre degradation and warm-up;
- fuel load and consumption;
- pit-stop loss and random pit-stop variation;
- traffic, VSC, Safety Car, and reliability-driven retirements;
- constrained strategy generation and Monte Carlo comparison;
- JSON race replays and interactive Plotly reports.

## Requirements

- Python 3.12 or newer;
- [`uv`](https://docs.astral.sh/uv/) for environment and dependency management;
- network access when downloading a new FastF1 session.

FastF1 is a required runtime dependency: it is the primary source of the
session data used to calibrate and evaluate strategies. Offline fixtures are
available for reproducible development and tests.

## Installation

```bash
git clone <repository-url>
cd race-strategy-simulator
uv sync
```

## Quick start with the bundled fixture

The following commands work without network access and use the example race
configuration and normalized session fixture:

```bash
uv run race-strategy validate --config configs/example_race.yaml

uv run race-strategy fetch-data \
  --year 2024 \
  --event Monza \
  --session R \
  --fixture configs/example_session_laps.yaml \
  --output data/session-laps.yaml

uv run race-strategy calibrate-config \
  --config configs/example_race.yaml \
  --input-path data/session-laps.yaml \
  --output data/calibrated-race.yaml

uv run race-strategy simulate \
  --config data/calibrated-race.yaml \
  --strategy medium-30-hard \
  --output data/replay.json \
  --plot data/replay.html
```

`simulate` prints the total race time. The optional JSON and HTML outputs
contain the complete lap-by-lap replay, including fuel, tyre age, penalties,
race-control state, and the strategy used.

## Real FastF1 workflow

Fetch a race session into a normalized YAML fixture. FastF1 stores downloaded
data in its cache directory, so subsequent runs can reuse it:

```bash
uv run race-strategy fetch-data \
  --year 2024 \
  --event Monza \
  --session R \
  --cache-dir .cache/fastf1 \
  --output data/monza-race.yaml
```

Then fit tyre parameters and apply them to a reusable race configuration:

```bash
uv run race-strategy calibrate-data \
  --input-path data/monza-race.yaml \
  --output data/monza-calibration.yaml

uv run race-strategy calibrate-config \
  --config configs/example_race.yaml \
  --input-path data/monza-race.yaml \
  --output data/monza-calibrated-race.yaml
```

Incomplete or non-finite FastF1 lap records are skipped during normalization.
If a remote session is unavailable, pass `--fixture` to `fetch-data` and use a
checked-in or locally generated normalized YAML fixture instead.

## Strategy analysis

Compare manually selected strategies with shared seeded scenarios:

```bash
uv run race-strategy compare \
  --config data/monza-calibrated-race.yaml \
  --strategy medium-30-hard \
  --strategy soft-20-medium \
  --runs 1000 \
  --seed 7
```

Generate legal strategies from the configured compound constraints:

```bash
uv run race-strategy generate-strategies \
  --config data/monza-calibrated-race.yaml \
  --min-stops 1 \
  --max-stops 2 \
  --pit-window 5 \
  --limit 20
```

Evaluate generated candidates with common random numbers:

```bash
uv run race-strategy optimize \
  --config data/monza-calibrated-race.yaml \
  --min-stops 1 \
  --max-stops 2 \
  --pit-window 5 \
  --strategies 100 \
  --runs 100 \
  --seed 7
```

Comparison and optimization reports include mean, median, standard deviation,
P10/P90, average pit stops, retirement rate, and probability of being fastest.

## Configuration and model details

The example configuration is [`configs/example_race.yaml`](configs/example_race.yaml).
The complete YAML schema, validation rules, and calibration workflow are in
[`docs/configuration.md`](docs/configuration.md).

Model equations and assumptions are documented in
[`docs/simulation-model.md`](docs/simulation-model.md). The architecture and
future prediction boundary are described in
[`docs/architecture.md`](docs/architecture.md) and
[`docs/prediction-model.md`](docs/prediction-model.md).

## Development

Run the checks with the repository environment:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest
uv run ruff check .
uv run mypy race_strategy
```

The pytest setting disables unrelated globally installed plugins. CI runs the
same test, lint, and type-check commands through
[GitHub Actions](.github/workflows/ci.yml).

## Project status

The offline simulation and calibration workflow is covered by automated tests.
Validation against a newly downloaded real FastF1 session remains dependent on
network access to the FastF1 schedule and data backends.
