# Project specification

Race Strategy Simulator is a configurable motorsport strategy simulation tool. It must keep domain models, simulation, strategy generation, analytics, prediction, and interfaces clearly separated.

The complete product requirements are recorded in `race_strategy_simulator.md`. The project must be implemented incrementally and remain runnable after every development step.

## Engineering rules

- Use Python 3.12+, `uv`, Pydantic, Typer, NumPy where useful, PyYAML, pytest, Ruff, and mypy.
- Keep business logic out of CLI and API handlers.
- Prefer small, typed, testable functions and explicit random-number generators.
- Separate model algorithms from configurable parameters.
- Add tests alongside new behavior and preserve deterministic reproducibility with explicit seeds.
- Do not implement prediction or multi-car features before the single-car simulator is stable.

## Documentation and code comments

All project documentation must be written in English.

Python code must be documented and commented according to the Google Python Style Guide:

- Use Google-style docstrings for public modules, classes, functions, and methods.
- Document arguments, return values, exceptions, and important side effects where applicable.
- Explain intent, assumptions, and non-obvious decisions; do not comment obvious syntax.
- Keep comments accurate, concise, and close to the code they explain.
- Use clear, complete English sentences in comments and docstrings.

Every Codex development run must read this file and `docs/development-log.md` before modifying the project. Every run must update `docs/development-log.md` in English with implemented work, modifications, tests, known issues, and the next recommended step.
