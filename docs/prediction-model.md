# Future prediction architecture

Prediction is intentionally not implemented in the current simulator phase.
This document defines the future data and evaluation boundaries without
introducing machine-learning dependencies into the physical simulation.

## Separation from simulation

The future `prediction/` package will consume normalized historical data and
produce probabilistic race-outcome estimates. It must not import simulation
internals to manufacture training labels or features. The simulator may later
consume a prediction as an input scenario, but the prediction package remains
independently testable.

The intended flow is:

```text
historical source adapters
        -> normalized historical dataset
        -> point-in-time feature builder
        -> chronological training/evaluation
        -> calibrated probabilistic predictor
```

## Point-in-time data

Every feature must have an explicit availability timestamp. Features must only
use information known at the prediction moment. For example:

- a pre-qualifying prediction may use historical pace, circuit, weather
  forecast, driver, and team features, but not qualifying results;
- a post-qualifying prediction may include qualifying position and lap times;
- a post-race label may include finishing position, points, podium, and win.

Future information must never leak into training features. The dataset should
retain source timestamps and the prediction cutoff used to build each row.

## Candidate features

Initial feature groups may include:

- driver and constructor historical pace;
- circuit-specific performance;
- tyre and stint observations from the data layer;
- qualifying and grid information when available at the cutoff;
- weather and race-control priors;
- reliability and recent retirement rates.

Features should be generated from normalized data adapters rather than directly
from FastF1 pandas objects. Missing values and data provenance must be explicit.

## Labels and outputs

The first prediction target should be a calibrated probability distribution for
win, podium, points, and finishing-position ranges. Outputs must include the
model version, training cutoff, feature cutoff, and calibration metadata.

The simulator can later evaluate conditional strategy scenarios by replacing or
augmenting race-condition priors. This is a downstream integration and must
not alter the baseline predictor's historical feature availability.

## Evaluation

Use chronological splits rather than random splits. A representative layout is
training on earlier seasons, validating on the next season, and testing on the
most recent unseen season. Report probabilistic metrics such as:

- log loss;
- Brier score;
- calibration error;
- top-k accuracy;
- finishing-position mean absolute error;
- rank correlation.

Winner accuracy alone is insufficient because the primary output is
probabilistic. Reliability diagrams and calibration checks should accompany
each model release.

## Planned package boundary

The future package may contain:

```text
prediction/
├── features.py
├── dataset.py
├── model.py
├── training.py
├── inference.py
├── calibration.py
└── evaluation.py
```

No prediction implementation is required until the single-car simulator and
historical data normalization are stable.
