# ARC Methodology

ARC (Age and Role Curves) is built around cohort-first analysis for fantasy football outcomes.

## Core philosophy

1. **Career year is the primary axis.**
   - Career phase often captures development and role progression better than age alone.
2. **Age bucket is secondary context.**
   - Age helps normalize within a career year cohort and identify early/late development paths.
3. **Cohort analysis precedes prediction.**
   - We establish reliable historical baselines before forecasting or labeling trajectories.
4. **Percentile and deviation framing.**
   - ARC emphasizes relative performance versus expected cohort outcomes.
5. **Trajectory modeling comes after stable baselines.**
   - Trajectory labels should be grounded in robust cohort distributions.

## Canonical table purposes

- `arc_player_seasons`: normalized player-season records with position, age bucket, career year, and seasonal outcome fields.
- `arc_player_weeks`: weekly records supporting volatility and event-rate metrics.
- `arc_cohort_baselines`: aggregate summary statistics by position + career year + age bucket.
- `arc_trajectory_scores`: expected-vs-actual scoring outputs plus percentile and label fields.

## PR1 scope note

PR1 defines structure, contracts, and documentation. Heavy ETL, full historical table construction, and production trajectory logic are deferred to follow-on PRs.
