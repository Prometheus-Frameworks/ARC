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
