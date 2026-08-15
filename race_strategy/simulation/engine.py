"""Single-car deterministic race simulator."""

import numpy as np

from race_strategy.models.race import RaceConfig
from race_strategy.models.race_control import (
    RaceControlEvent,
    RaceControlState,
)
from race_strategy.models.result import LapResult, RaceResult, StintResult
from race_strategy.models.strategy import Strategy

from .lap_model import calculate_lap_time
from .pitstop import pit_stop_loss


def _race_control_effect(
    race: RaceConfig, events: list[RaceControlEvent], lap: int
) -> tuple[RaceControlState, float, float]:
    """Return state, lap-time multiplier, and pit-loss multiplier for a lap."""
    state = RaceControlState.GREEN
    for event in events:
        if event.applies_to(lap):
            state = event.state
    if state is RaceControlState.VSC:
        return state, race.circuit.vsc_lap_time_multiplier, 0.75
    if state is RaceControlState.SAFETY_CAR:
        return state, race.circuit.safety_car_lap_time_multiplier, 0.5
    return state, 1.0, 1.0


def _build_race_control_events(
    race: RaceConfig, rng: np.random.Generator
) -> list[RaceControlEvent]:
    """Combine static events with at most one seeded random event."""
    events = list(race.race_control)
    randomization = race.race_control_random
    draw = rng.random()
    if draw >= (randomization.vsc_probability + randomization.safety_car_probability):
        return events
    state = (
        RaceControlState.VSC
        if draw < randomization.vsc_probability
        else RaceControlState.SAFETY_CAR
    )
    latest_start = max(1, race.laps - randomization.duration + 1)
    start_lap = int(rng.integers(1, latest_start + 1))
    events.append(
        RaceControlEvent(
            state=state,
            start_lap=start_lap,
            end_lap=min(race.laps, start_lap + randomization.duration - 1),
        )
    )
    return events


def simulate_race(
    race: RaceConfig, strategy: Strategy, seed: int | None = None
) -> RaceResult:
    """Simulate one race using a strategy and an optional seeded RNG."""
    race.validate_strategy(strategy)
    rng = np.random.default_rng(seed)
    race_control_events = _build_race_control_events(race, rng)
    compound = strategy.starting_compound.lower()
    tyre_age = 0
    laps: list[LapResult] = []
    stints: list[StintResult] = []
    stint_start = 1
    failure_lap: int | None = None
    stop_by_lap = {stop.lap: stop.compound.lower() for stop in strategy.stops}
    for lap in range(1, race.laps + 1):
        if rng.random() >= race.car.reliability:
            failure_lap = lap
            break
        if lap in stop_by_lap:
            stints.append(
                StintResult(compound=compound, start_lap=stint_start, end_lap=lap - 1)
            )
            compound = stop_by_lap[lap]
            tyre_age = 0
            stint_start = lap
        tyre_age += 1
        fuel = max(
            0.0, race.car.initial_fuel - race.car.fuel_consumption_per_lap * (lap - 1)
        )
        variation = float(rng.normal(0.0, race.driver.lap_time_variance))
        tyre = next(
            value for name, value in race.tyres.items() if name.lower() == compound
        )
        race_control, lap_multiplier, pit_multiplier = _race_control_effect(
            race, race_control_events, lap
        )
        traffic_penalty = (
            race.circuit.traffic_penalty
            if rng.random() < race.circuit.traffic_probability
            else 0.0
        )
        lap_time, degradation, warmup, fuel_penalty = calculate_lap_time(
            race, tyre, tyre_age, fuel, variation, lap_multiplier
        )
        stop_loss = (
            pit_stop_loss(
                race.circuit.pit_lane_loss,
                variance=float(rng.normal(0.0, race.car.pit_stop_variance)),
                race_control_multiplier=pit_multiplier,
            )
            if lap in stop_by_lap
            else 0.0
        )
        laps.append(
            LapResult(
                lap=lap,
                lap_time=lap_time + traffic_penalty + stop_loss,
                tyre=compound,
                tyre_age=tyre_age,
                fuel=fuel,
                degradation_penalty=degradation,
                warmup_penalty=warmup,
                fuel_penalty=fuel_penalty,
                traffic_penalty=traffic_penalty,
                pit_stop_loss=stop_loss,
                race_control=race_control.value,
            )
        )
    if laps:
        stints.append(
            StintResult(compound=compound, start_lap=stint_start, end_lap=laps[-1].lap)
        )
    finished = failure_lap is None
    total_time = sum(item.lap_time for item in laps)
    warnings = [] if finished else [f"car retired on lap {failure_lap}"]
    if not finished:
        total_time += race.car.retirement_penalty
    return RaceResult(
        total_time=total_time,
        strategy=strategy,
        laps=laps,
        stints=stints,
        pit_stops=sum(item.pit_stop_loss > 0 for item in laps),
        finished=finished,
        failure_lap=failure_lap,
        warnings=warnings,
    )
