# Simulation model

The simulator models one car over a configured number of laps. It is
deterministic when the same configuration, strategy, and random seed are used.
The implementation deliberately favors transparent, independently testable
effects over telemetry-level precision.

## Lap time

For a completed lap, the base time is calculated as:

```text
base_lap_time
+ car.base_pace
+ driver.pace_delta
+ tyre.base_delta
+ degradation_penalty
+ warmup_penalty
+ fuel_penalty
+ random_variation
```

The race-control multiplier is then applied to this sum. Traffic and pit-stop
loss are added afterwards, because they are modeled as time losses external to
the car's clean-lap pace.

The random variation is sampled from a normal distribution with mean zero and
standard deviation `driver.lap_time_variance`. The explicit NumPy generator is
seeded by `simulate_race`.

## Tyres

Tyre age starts at one on the first lap of a stint and resets to zero before
the first lap after a pit stop. Linear degradation is:

```text
degradation_rate * tyre_age * driver.tyre_management_factor
```

When `tyre_age >= cliff_lap`, `cliff_penalty` is added. The warm-up penalty is
added while `tyre_age <= warmup_laps`.

The calibration pipeline fits:

```text
observed_lap_time = base_lap_time + degradation_rate * tyre_age
```

and converts the fitted intercept into a compound `base_delta` relative to the
configured race baseline.

## Fuel

Fuel at lap `n` is:

```text
max(0, initial_fuel - fuel_consumption_per_lap * (n - 1))
```

The current model applies `fuel * fuel_effect_per_kg` as a lap-time penalty.
Fuel is reported in every `LapResult` so a later calibration can replace this
linear approximation without changing result consumers.

## Pit stops

A pit stop is scheduled at the configured lap and contributes:

```text
(pit_lane_loss + stationary_time + pit_stop_noise) * race_control_multiplier
```

`pit_stop_noise` is sampled from a zero-mean normal distribution whose standard
deviation is `car.pit_stop_variance`. The current stationary-time default is
2.5 seconds. The tyre age resets on the pit-stop lap, so the new compound is
used for that lap's result.
Strategies must schedule pit stops after lap one and before the final lap, so
every configured stint contains at least one completed lap.
`RaceConfig.validate_strategy` also enforces each selected compound's
`minimum_stint` and `maximum_stint` limits, including for manually written
strategies.

## Race control and traffic

Race-control events use inclusive lap intervals. GREEN uses a multiplier of
1.0, VSC uses the circuit's VSC multiplier and 75% pit loss, and SAFETY_CAR
uses the circuit's Safety Car multiplier and 50% pit loss. If intervals
overlap, the last matching event in the configuration wins.

Traffic is sampled independently on each lap. If a random draw is below
`traffic_probability`, `traffic_penalty` is added to that lap and recorded in
the result.

The optional `race_control_random` configuration performs one mutually
exclusive seeded draw per simulation. It can create a VSC or Safety Car event
with a random valid start lap and configured duration. Static configured
events remain active as well; if intervals overlap, the last matching event
still wins.

## Reliability and DNF

Reliability is checked before each lap. A failed check ends the simulation at
that lap, marks `RaceResult.finished` false, and records `failure_lap` and a
warning. `car.retirement_penalty` is added to the partial race time so a DNF is
not treated as a deceptively fast result during strategy comparison.

## Reproducibility and outputs

`RaceResult` contains the planned strategy, lap results, stint summaries, actual
pit stops, race completion status, and warnings. It can be serialized with
Pydantic to JSON.
The CLI can export this replay and produce a self-contained Plotly HTML report.
