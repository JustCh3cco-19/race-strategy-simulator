# Development log

## 2026-08-15 - Simulation foundation

### Implemented

- Added NumPy and FastF1 as runtime dependencies; FastF1 is required as the primary strategy-data source.
- Added normalized `SessionLap` data plus offline YAML loading and a lazy FastF1 adapter.
- Added normalized fixture export and the `fetch-data` CLI command for FastF1 sessions.
- Added first-order compound calibration and the `calibrate-data` CLI command.
- Added calibration application to `RaceConfig` and the `calibrate-config` CLI command.
- Added configurable GREEN, VSC, and SAFETY_CAR events with lap and pit-stop effects.
- Added constrained strategy generation and the `generate-strategies` CLI command.
- Added Monte Carlo strategy ranking and the `optimize` CLI command.
- Added shared-scenario fastest-strategy probabilities to optimization results.
- Added standard deviation, percentile, and average pit-stop metrics to CLI reports.
- Added Monte Carlo retirement-rate metrics to strategy reports.
- Added reusable `analytics.metrics` aggregation for race-result collections.
- Added `docs/configuration.md` with YAML fields, constraints, and calibration workflow.
- Hardened FastF1 normalization against incomplete and non-finite lap records.
- Corrected pit-stop variance to be sampled noise rather than a fixed offset.
- Added configurable seeded traffic probability and lap-time penalties.
- Added reliability-driven retirements with explicit DNF results and penalties.
- Added seeded stochastic VSC/Safety Car generation for Monte Carlo runs.
- Added validation for race-control bounds and first-lap pit-stop strategies.
- Corrected strategy generation to exclude first-lap pit stops.
- Extended manual strategy validation to enforce compound stint limits.
- Added JSON race-replay export from the `simulate` command.
- Added the planned strategy metadata to serialized `RaceResult` replays.
- Expanded the example race configuration with all supported stochastic and reliability parameters.
- Added Plotly HTML replay reports with lap-time, fuel, tyre-age, and penalty plots.
- Added GitHub Actions CI for locked uv installs, pytest, Ruff, and mypy.
- Added `docs/simulation-model.md` with equations, assumptions, and output semantics.
- Added `docs/prediction-model.md` describing future point-in-time features and evaluation.
- Updated `compare` to use shared Monte Carlo scenarios and fastest probabilities.
- Added composable tyre degradation, warm-up, lap-time, and pit-stop models.
- Added deterministic single-car simulation with lap, stint, fuel, tyre, and pit-stop results.
- Added seeded Monte Carlo summaries and regression tests.
- Added offline FastF1-shaped fixture and round-trip serialization tests.
- Added calibration regression tests for fitted degradation parameters.
- Added round-trip tests for calibrated race configurations.
- Added race-control simulation regression tests.
- Added a regression test for reduced pit-stop loss under VSC.
- Added generator tests for stint constraints and invalid bounds.
- Added deterministic ranking and strategy-formatting tests.
- Added regression coverage for fastest-strategy probabilities.
- Added regression coverage for average pit-stop metrics.
- Added regression coverage for reproducible traffic penalties.
- Added regression coverage for retirement handling and DNF penalties.
- Added regression coverage for seeded random race-control events.
- Added race-result JSON round-trip regression coverage.
- Added regression coverage for interactive replay report generation.
- Added `simulate` and `compare` CLI commands for single runs and strategy comparisons.

### Modified

- Added `race_strategy/data`, `race_strategy/simulation`, and result models.
- Added pytest configuration to avoid the unrelated ROS `launch_testing` plugin.
- Added Google-style explanatory comments to the test assertions and fixtures.
- Updated the README to document the current simulator commands and test setup.
- Updated the README and project metadata to make FastF1 a mandatory dependency.

### Tests

- Ruff, mypy, and tests should be run with the repository environment and external pytest plugin autoload disabled.
- Completed an offline end-to-end smoke test: fixture export, calibration,
  calibrated config, strategy generation, optimization, JSON replay, and HTML plot.
- Attempted a real 2024 Monza FastF1 session load; all available schedule
  backends were unreachable in the current environment.
- Added an isolated FastF1 adapter test using a session-shaped fixture, so
  normalization remains covered without network access.
- Reworked the README into a task-oriented guide covering installation,
  offline and real FastF1 workflows, strategy analysis, and project status.

### Known issues

- The checked-in local environment is stale and cannot currently be repaired because uv cannot write its global cache.
- FastF1 normalization still needs validation against a downloaded real session before calibration work.
- The current environment cannot reach FastF1 schedule backends; real-session validation remains pending network access.

### Next recommended step

- Validate normalization and calibrated simulation against a downloaded real
  FastF1 session, then calibrate fuel effects and add stochastic race-control
  events.

## 2026-08-14 - Development session

### Implemented

- Documented all Python modules, public classes, functions, and methods with concise Google-style docstrings in English.
- Added an explanatory comment for the YAML-to-model payload transformation.

### Modified

- Updated source models, configuration loading, CLI code, and tests with English documentation.

### Tests

- Not run yet; documentation-only changes should be verified with the project's test and lint commands.

### Known issues

- The existing dependency-cache permission issue may still prevent `uv` commands from running.

### Next recommended step

- Integrate FastF1 as the primary real-data source, normalize session data, and define a cached offline mode.

### Implemented

- Created the uv-based project foundation.
- Added Pydantic models for races, circuits, cars, drivers, tyres, and strategies.
- Added YAML configuration loading and the `validate` CLI command.
- Added an example configuration and initial tests.

### Modified

- Updated the README and `.gitignore`.
- Added persistent project specification and architecture documentation.
- Standardized project documentation in English.
- Added the requirement to follow the Google Python Style Guide for comments and docstrings.

### Tests

- `uv sync` was attempted but could not complete because the environment denied access to uv's cache directory.
- Test, lint, and type-check commands remain to be run after dependency synchronization.

### Known issues

- The simulation engine has not been implemented yet.
- The environment must permit uv cache access before dependencies can be synchronized.

### Next recommended step

- Integrate FastF1 data before implementing the physical simulation, then calibrate and test tyre degradation, fuel, and lap-time calculations.
