# ARC Roadmap

## PR2: Historical cohort table construction

- Build `arc_player_seasons` from historical player-season sources.
- Build `arc_player_weeks` from historical weekly game logs.
- Standardize IDs, position normalization, and age/career annotations.

## PR3: Baseline metric computation

- Compute `arc_cohort_baselines` by position + career year + age bucket.
- Add cohort sample validation checks.
- Export baseline summary artifacts for downstream consumption.

## PR4: Trajectory scoring

- Compute `arc_trajectory_scores` with expected-vs-actual deltas.
- Add percentile/deviation framing and trajectory labels.
- Introduce QA checks for edge cohorts and sparse samples.

## Optional future expansions

- Draft capital as a conditioning variable
- Usage archetype layers (target share, touch share, etc.)
- Comparable player trajectory engine
- Next-year hit-rate tables
