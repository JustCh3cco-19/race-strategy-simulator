"""Tests for deterministic simulation components."""

from pathlib import Path

from race_strategy.config import load_race_config
from race_strategy.models.race_control import RaceControlRandomization
from race_strategy.models.strategy import PitStop, Strategy
from race_strategy.simulation.degradation import degradation_penalty
from race_strategy.simulation.engine import simulate_race
from race_strategy.simulation.monte_carlo import monte_carlo


def test_simulation_produces_laps_and_stints() -> None:
    """A valid strategy produces one result for every race lap."""
    race = load_race_config(Path("configs/example_race.yaml"))
    result = simulate_race(
        race,
        Strategy(starting_compound="medium", stops=[PitStop(lap=30, compound="hard")]),
    )
    # The zero-based index 29 represents the one-based pit-stop lap 30.
    assert len(result.laps) == race.laps
    assert len(result.stints) == 2
    assert result.laps[29].pit_stop_loss > 0


def test_seeded_simulation_is_reproducible() -> None:
    """The same seed produces identical serialized output."""
    race = load_race_config(Path("configs/example_race.yaml"))
    strategy = Strategy(starting_compound="medium")
    # Comparing serialized models also verifies every lap-level output field.
    assert (
        simulate_race(race, strategy, seed=42).model_dump()
        == simulate_race(race, strategy, seed=42).model_dump()
    )


def test_race_result_json_round_trip() -> None:
    """Serialize and restore the complete replay without data loss."""
    race = load_race_config(Path("configs/example_race.yaml"))
    strategy = Strategy(starting_compound="medium")
    result = simulate_race(race, strategy, seed=42)

    restored = type(result).model_validate_json(result.model_dump_json())

    assert restored == result
    assert restored.strategy == strategy


def test_degradation_cliff_is_applied() -> None:
    """The cliff penalty is added at the configured age."""
    race = load_race_config(Path("configs/example_race.yaml"))
    tyre = race.tyres["medium"]
    # The configured medium-tyre cliff starts at age 28.
    assert degradation_penalty(tyre, 28) > degradation_penalty(tyre, 27)


def test_monte_carlo_is_reproducible() -> None:
    """Monte Carlo summaries are stable for a fixed seed."""
    race = load_race_config(Path("configs/example_race.yaml"))
    strategy = Strategy(starting_compound="medium")
    # A fixed master seed must reproduce the complete summary exactly.
    assert monte_carlo(race, strategy, 5, 7) == monte_carlo(race, strategy, 5, 7)


def test_race_control_changes_lap_result() -> None:
    """Record configured VSC and Safety Car states on affected laps."""
    race = load_race_config(Path("configs/example_race.yaml"))
    result = simulate_race(race, Strategy(starting_compound="medium"))

    assert result.laps[19].race_control == "VSC"
    assert result.laps[39].race_control == "SAFETY_CAR"
    assert result.laps[0].race_control == "GREEN"


def test_race_control_reduces_pit_stop_loss() -> None:
    """Apply the configured pit-loss reduction during a VSC pit stop."""
    race = load_race_config(Path("configs/example_race.yaml"))
    result = simulate_race(
        race,
        Strategy(starting_compound="medium", stops=[PitStop(lap=20, compound="hard")]),
    )

    assert result.laps[19].pit_stop_loss < race.circuit.pit_lane_loss + 2.5


def test_pit_stop_variance_is_seeded_noise() -> None:
    """Sample pit-stop noise reproducibly instead of using a fixed offset."""
    race = load_race_config(Path("configs/example_race.yaml"))
    variable_race = race.model_copy(
        update={"car": race.car.model_copy(update={"pit_stop_variance": 1.0})}
    )
    strategy = Strategy(
        starting_compound="medium", stops=[PitStop(lap=20, compound="hard")]
    )

    first = simulate_race(variable_race, strategy, seed=42)
    second = simulate_race(variable_race, strategy, seed=42)

    assert first.model_dump() == second.model_dump()
    assert first.laps[19].pit_stop_loss != race.circuit.pit_lane_loss + 2.5


def test_traffic_penalty_is_applied_reproducibly() -> None:
    """Apply configured traffic penalties through the seeded random generator."""
    race = load_race_config(Path("configs/example_race.yaml"))
    traffic_race = race.model_copy(
        update={
            "circuit": race.circuit.model_copy(
                update={"traffic_probability": 1.0, "traffic_penalty": 0.8}
            )
        }
    )
    result = simulate_race(traffic_race, Strategy(starting_compound="medium"), seed=4)

    assert all(lap.traffic_penalty == 0.8 for lap in result.laps)


def test_unreliable_car_retires_with_penalty() -> None:
    """Represent a retirement explicitly and penalize its result time."""
    race = load_race_config(Path("configs/example_race.yaml"))
    unreliable_race = race.model_copy(
        update={"car": race.car.model_copy(update={"reliability": 0.0})}
    )

    result = simulate_race(
        unreliable_race, Strategy(starting_compound="medium"), seed=4
    )

    assert not result.finished
    assert result.failure_lap == 1
    assert result.total_time == unreliable_race.car.retirement_penalty
    assert result.warnings == ["car retired on lap 1"]


def test_random_race_control_is_seeded() -> None:
    """Generate reproducible race-control events from configuration probabilities."""
    race = load_race_config(Path("configs/example_race.yaml"))
    random_race = race.model_copy(
        update={
            "race_control_random": RaceControlRandomization(
                vsc_probability=1.0, duration=2
            ),
        }
    )

    first = simulate_race(random_race, Strategy(starting_compound="medium"), seed=9)
    second = simulate_race(random_race, Strategy(starting_compound="medium"), seed=9)

    assert first.model_dump() == second.model_dump()
    assert any(lap.race_control == "VSC" for lap in first.laps)
