# Architecture

The current implementation is split into Pydantic domain models in
`race_strategy/models`, configuration and data adapters in `config.py` and
`data/`, simulation algorithms in `simulation/`, strategy generation and
evaluation in `strategy/`, and reports in `analytics/`. The CLI in `cli.py` is
thin and delegates business logic to these packages.

The FastF1 adapter normalizes observed laps into internal models and supports
YAML fixtures for offline reproducibility. The simulator consumes only the
normalized domain/configuration models, so it remains independent from
FastF1's pandas objects.

The YAML schema and validation constraints are documented in
`configuration.md`.

The future [`prediction-model.md`](prediction-model.md) package must remain
independent from the physical simulation engine. The optional API/dashboard
layer must likewise delegate to
the same domain and simulation services rather than duplicate them.

The primary flow is:

```text
FastF1 or YAML fixture
        -> normalized session laps
        -> calibration
        -> RaceConfig
        -> deterministic simulation / Monte Carlo
        -> strategy ranking and replay reports
```

Public Python APIs use Google-style docstrings. Comments explain assumptions and intent, especially where a mathematical model is not self-evident.
