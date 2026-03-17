# Metric Definitions (PR1)

This document defines ARC's initial metric vocabulary. Threshold values are provisional defaults in PR1.

## Core metrics

- **PPG (points per game)**
  - `season_points / games_played` for season-level analysis.
- **Spike week rate**
  - Share of player-weeks classified as spikes using position-specific weekly finish cutoffs.
- **Dud week rate**
  - Share of player-weeks classified as duds using position-specific weekly finish cutoffs.
- **Elite finish rate**
  - Cohort share of player-seasons ending inside position-level elite cutoff.
- **Starter finish rate**
  - Cohort share of player-seasons ending inside starter-level cutoff.

## Trajectory metrics

- **Delta vs expected**
  - `actual_ppg - expected_ppg` relative to cohort baseline.
- **Percentile within cohort**
  - Percentile rank of actual performance among cohort peers.
- **Trajectory label**
  - Categorical descriptor (for example: rising, stable, declining) based on deviation and percentile context.

## PR1 provisional threshold note

Current spike/dud and elite/starter cutoffs are initial defaults intended to validate structure. They will be calibrated in future PRs using historical distributions.
