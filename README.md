# ARC: Age and Role Curves

ARC is a historical fantasy football cohort engine designed for research-grade analysis of player outcomes over time. It models performance relative to peers grouped by **position**, **career year**, and **age bucket**.

## Quick start

1. Place raw weekly player history under `data/raw/`.
   - Default path: `data/raw/player_weekly_history.csv`
   - Supported formats: `.csv` and `.parquet`
2. Run cohort build:

```bash
python -m arc.cli build-cohorts --input data/raw/player_weekly_history.csv
```

3. Outputs are written to `outputs/cohort_tables/`:
   - `arc_player_weeks.csv`
   - `arc_player_seasons.csv`
   - parquet mirrors when a parquet engine (for example `pyarrow`) is installed

Other useful commands:

```bash
python -m arc.cli info
python -m arc.cli validate-config
```

## Canonical ARC tables

- `arc_player_weeks`: one row per player-week including weekly positional finish and spike/dud flags.
- `arc_player_seasons`: one row per player-season including games played, season points, ppg, and seasonal positional finish.

## Roadmap

- **PR2:** Build historical player-week and player-season cohort tables.
- **PR3:** Compute cohort baselines by position/career-year/age-bucket slices.
- **PR4:** Add trajectory scoring and expected-vs-actual labels.
