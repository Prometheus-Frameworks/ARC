# ARC Methodology

## PR2 historical cohort pipeline

PR2 builds two canonical historical outputs from weekly source data:

- `arc_player_weeks`: one row per player-week-season.
- `arc_player_seasons`: one row per player-season aggregated from weekly rows.

Default source contract:

- Input path: `data/raw/player_weekly_history.csv` (or parquet equivalent).
- Required concepts: `player_id`, `player_name`, `season`, `week`, `position`, `team`, `fantasy_points`.
- Supported aliases are normalized in code (for example `playerid` -> `player_id`, `pos` -> `position`, `points` -> `fantasy_points`).

## Career year assignment (PR2 rule)

Career year is assigned **per player + position**:

1. Sort seasons chronologically.
2. Define the first observed season as the first season with at least one weekly row in the dataset.
3. Assign `career_year = 1` in that season and increment by one each season.

Important caveat: ARC career year in PR2 is based on first observed season in available data. It may be refined later with debut filters or minimum participation thresholds.

## Age handling and age buckets

Age is resolved in this order:

1. Use `age` if supplied.
2. Otherwise derive age from `birth_date` using a season anchor date of September 1 (`season-09-01`).
3. If neither is available, keep `age` null.

If age is null, `age_bucket` remains null.

Default buckets:

- `<22`
- `22-23`
- `24-25`
- `26-27`
- `28-29`
- `30+`

## Weekly finish computation

For each `season + week + position` group:

- Rank players by `fantasy_points` descending.
- Use `rank(method="min")` for tie handling.
- Assign result to `weekly_pos_finish`.
- Only rows with non-null `fantasy_points` are ranked.

Spike/dud flags are derived from positional finish thresholds in config.

## Season finish computation

`arc_player_seasons` is aggregated from `arc_player_weeks`.

Per player-season:

- `games_played`: count of weeks with non-null `fantasy_points`
- `season_points`: sum of `fantasy_points`
- `ppg`: `season_points / games_played` (null if games played is zero)

Season positional ranking:

- Rank by `season_points` within `season + position` using descending `rank(method="min")`.
- Output as `positional_finish`.

Tier flags:

- `top_tier_finish`: true when seasonal finish is inside elite cutoff.
- `starter_tier_finish`: true when seasonal finish is inside starter cutoff (includes top-tier finishes).
