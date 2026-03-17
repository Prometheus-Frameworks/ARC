# Metric Definitions

## Weekly table metrics (`arc_player_weeks`)

- **weekly_pos_finish**
  - Positional finish rank for a player within the same `season + week + position`, ranked by weekly fantasy points descending with `min` tie ranking.
- **spike_flag**
  - Boolean indicating a week with finish at or above the position spike threshold (for example QB <= 8, RB/WR <= 12, TE <= 6).
- **dud_flag**
  - Boolean indicating a week with finish below the position dud threshold (for example QB > 18, RB/WR > 36, TE > 18).

## Season table metrics (`arc_player_seasons`)

- **games_played**
  - Count of weekly rows with non-null fantasy points for the player-season.
- **season_points**
  - Sum of weekly fantasy points across all valid weeks in a player-season.
- **ppg**
  - `season_points / games_played` (null when `games_played` is zero).
- **positional_finish**
  - Seasonal finish rank within `season + position`, ranked by `season_points` descending with `min` tie ranking.
- **top_tier_finish**
  - True when `positional_finish` is at or above position elite season threshold.
- **starter_tier_finish**
  - True when `positional_finish` is at or above starter threshold (includes top-tier seasons).

## Baseline summary metrics (`arc_cohort_baselines`, `arc_career_year_baselines`)

- **sample_size**
  - Count of player-season rows in the cohort group.
- **avg_ppg**
  - Mean of player-season `ppg` values (nulls ignored).
- **median_ppg**
  - Median of player-season `ppg` values (nulls ignored).
- **ppg_std**
  - Sample standard deviation of player-season `ppg` (`ddof=1`; null for cohorts with fewer than two non-null values).
- **avg_season_points**
  - Mean of player-season `season_points` values.
- **median_season_points**
  - Median of player-season `season_points` values.
- **avg_games_played**
  - Mean of player-season `games_played`.
- **spike_rate**
  - Mean of per-player-season spike rates where per-player-season rate is `spike_weeks / games_played`.
- **dud_rate**
  - Mean of per-player-season dud rates where per-player-season rate is `dud_weeks / games_played`.
- **elite_finish_rate**
  - Mean of `top_tier_finish` interpreted as 1/0.
- **starter_finish_rate**
  - Mean of `starter_tier_finish` interpreted as 1/0.
- **is_small_sample**
  - Boolean flag indicating `sample_size < small_sample_threshold`.
- **small_sample_threshold**
  - Threshold used for the small-sample flag; defaults to `10`.
