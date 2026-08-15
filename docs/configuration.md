# YAML configuration

`load_race_config` reads a YAML mapping with the sections shown below and
validates it with Pydantic. The bundled [example configuration](../configs/example_race.yaml)
is a runnable reference.

## Race section

```yaml
race:
  name: Example Grand Prix
  laps: 58
  baseline_lap_time: 90.0
```

`name` must be non-empty. `laps` and `baseline_lap_time` must be positive.

## Circuit section

Required fields are `name` and positive `pit_lane_loss`. Optional fields are:

| Field | Meaning | Default |
| --- | --- | ---: |
| `safety_car_lap_time_multiplier` | Clean-lap multiplier under Safety Car | `1.25` |
| `vsc_lap_time_multiplier` | Clean-lap multiplier under VSC | `1.10` |
| `overtaking_difficulty` | Normalized circuit difficulty | `0.5` |
| `traffic_probability` | Per-lap traffic probability | `0.0` |
| `traffic_penalty` | Added seconds when traffic occurs | `0.0` |

Probabilities must be between zero and one. Traffic is sampled from the
simulation seed.

## Car section

Required positive fields are `fuel_effect_per_kg`, `initial_fuel`, and
`fuel_consumption_per_lap`. `base_pace` defaults to zero. The optional fields
are:

| Field | Meaning | Default |
| --- | --- | ---: |
| `pit_stop_variance` | Standard deviation of pit-stop noise in seconds | `0` |
| `reliability` | Probability of surviving each lap | `1` |
| `retirement_penalty` | Seconds added to a DNF result | `300` |

## Driver section

`name` is required. `pace_delta` defaults to zero, `lap_time_variance` defaults
to zero, `tyre_management_factor` defaults to one, and `consistency` defaults
to one. Variance and management factor must be positive or non-negative as
appropriate; consistency is constrained to zero through one.

## Tyres section

`tyres` must contain at least one named compound. Each compound supports:

| Field | Meaning |
| --- | --- |
| `name` | Display name |
| `base_delta` | Pace offset relative to race baseline |
| `degradation_rate` | Linear seconds per tyre-age unit |
| `warmup_penalty` | Added warm-up seconds |
| `warmup_laps` | Number of warm-up laps |
| `cliff_lap` | Age at which the cliff starts, or null |
| `cliff_penalty` | Added cliff seconds |
| `minimum_stint` | Minimum legal stint length |
| `maximum_stint` | Maximum legal stint length, or null |

`degradation_rate`, penalties, and stint minimums must not be negative. A
maximum stint, when present, must be at least the minimum stint.

## Race-control sections

Static events use inclusive lap intervals:

```yaml
race_control:
  - state: VSC
    start_lap: 20
    end_lap: 21
```

Valid states are `GREEN`, `VSC`, and `SAFETY_CAR`. Event intervals must fit
within the race. Overlapping intervals are allowed; the last matching event in
the YAML list wins.

Monte Carlo race-control can add one random event per simulation:

```yaml
race_control_random:
  vsc_probability: 0.20
  safety_car_probability: 0.10
  duration: 3
```

The two probabilities must sum to at most one, and duration must fit within
the race. The event type and start lap are derived from the simulation seed.

## Strategies

Strategies are supplied to the CLI in compact form, for example
`medium-30-hard`, meaning medium at the start and a switch to hard on lap 30.
Pit stops must occur after lap one and before the final lap. Every stint must
respect the selected compound's minimum and maximum lengths.

## Calibration workflow

Use normalized session data to create calibrated parameters and apply them to
a copy of a race configuration:

```bash
uv run race-strategy calibrate-data \
  --input-path data/session.yaml \
  --output data/calibration.yaml
uv run race-strategy calibrate-config \
  --config configs/example_race.yaml \
  --input-path data/session.yaml \
  --output data/calibrated-race.yaml
```

The resulting calibrated YAML remains a normal race configuration and can be
passed to `simulate`, `compare`, and `optimize`.
