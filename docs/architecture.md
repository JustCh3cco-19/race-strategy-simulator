# Architecture

The foundation phase contains Pydantic models in `src/race_strategy/models`, YAML loading in `config.py`, and a thin CLI in `cli.py`. Domain logic must not be placed in CLI commands.

Simulation will be added in separate packages (`simulation`, `strategy`, and `analytics`). The future `prediction` package must remain independent from the physical simulation engine.

Public Python APIs use Google-style docstrings. Comments explain assumptions and intent, especially where a mathematical model is not self-evident.
