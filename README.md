# Race Strategy Simulator

CI workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml)

A configurable and testable motorsport race strategy simulator with deterministic single-car simulation, strategy comparison, and FastF1 data loading.

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
uv run race-strategy simulate --config configs/example_race.yaml --strategy medium-30-hard
uv run race-strategy simulate --config configs/example_race.yaml \
  --strategy medium-30-hard --output data/replay.json
uv run race-strategy simulate --config configs/example_race.yaml \
  --strategy medium-30-hard --plot data/replay.html
uv run race-strategy compare --config configs/example_race.yaml \
  --strategy medium-30-hard --strategy soft-20-medium --runs 1000
uv run race-strategy fetch-data --year 2025 --event Monza \
  --session R --output data/monza-race.yaml
uv run race-strategy calibrate-data \
  --input-path data/monza-race.yaml \
  --output data/monza-calibration.yaml
uv run race-strategy calibrate-config \
  --config configs/example_race.yaml \
  --input-path data/monza-race.yaml \
  --output data/monza-calibrated-race.yaml
uv run race-strategy generate-strategies \
  --config data/monza-calibrated-race.yaml \
  --min-stops 1 --max-stops 2 --pit-window 5 --limit 20
uv run race-strategy optimize \
  --config data/monza-calibrated-race.yaml \
  --min-stops 1 --max-stops 2 --pit-window 5 \
  --strategies 100 --runs 100
```

FastF1 is a required runtime dependency because it is the primary source for
session data used to build and evaluate strategies. The `fetch-data` command
stores normalized laps in a YAML fixture; pass `--fixture` to convert an
existing fixture without accessing FastF1.
The `calibrate-data` command fits a first-order tyre degradation model from
the normalized lap data.
Incomplete or non-finite lap records from FastF1 session tables are skipped
during normalization.
Use `calibrate-config` to apply those fitted values directly to a reusable
race configuration consumed by `simulate` and `compare`.
`generate-strategies` enumerates legal compound and pit-window combinations
using the configured stint constraints.
`optimize` evaluates generated candidates with Monte Carlo simulation and
prints them ordered by mean race time, including standard deviation, P10/P90,
average pit stops, and each candidate's probability of being fastest across
shared race scenarios.
Reports also include the observed DNF rate for each strategy.
The reusable analytics layer exposes the same aggregate metrics for result
collections and future report formats.
`compare` uses the same shared-scenario method for manually supplied
strategies.
Race configurations can also define inclusive `race_control` lap intervals
with `VSC` or `SAFETY_CAR`; these alter lap pace and reduce pit-stop loss.
The `race_control_random` section can additionally define seeded VSC/Safety Car
probabilities and event duration for Monte Carlo runs.
Circuit configurations may define `traffic_probability` and
`traffic_penalty`; traffic is sampled reproducibly from the simulation seed
and is included in every affected `LapResult`.
The bundled example configuration also shows the neutral defaults for traffic,
vehicle reliability, DNF penalty, and stochastic race-control settings.
Vehicle reliability is also simulated; retirements are represented in
`RaceResult` and receive the configured `retirement_penalty` so they cannot
artificially appear faster than finished races.
Pass `--output` to `simulate` to save the complete serializable race replay as
JSON, including the strategy that produced it.
Pass `--plot` to generate a self-contained interactive Plotly HTML report.

## Development

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest
uv run ruff check .
uv run mypy race_strategy
```

The pytest command disables unrelated globally installed plugins so that the
project test suite runs in a clean, reproducible environment.

The roadmap, architecture, and equations are documented in
`docs/project-spec.md`, `docs/architecture.md`, and
[`docs/simulation-model.md`](docs/simulation-model.md).
The future prediction boundary is documented in
[`docs/prediction-model.md`](docs/prediction-model.md).
The complete YAML schema and calibration workflow are documented in
[`docs/configuration.md`](docs/configuration.md).
Continuous integration runs the same pytest, Ruff, and mypy checks through
`uv` on every push and pull request.
