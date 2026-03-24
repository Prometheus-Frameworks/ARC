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

3. Build baseline summary tables from cohort outputs:

```bash
python -m arc.cli build-baselines
```

4. Build the promoted downstream handoff artifact:

```bash
python -m arc.cli build-promoted-handoff
```

5. Outputs are written to `outputs/cohort_tables/`, `outputs/summary_tables/`, and `outputs/promoted/`:
   - `arc_player_weeks.csv`
   - `arc_player_seasons.csv`
   - `arc_promoted_handoff.csv` (canonical downstream contract)
   - parquet mirrors for cohort/baseline tables when a parquet engine (for example `pyarrow`) is installed

Other useful commands:

```bash
python -m arc.cli info
python -m arc.cli validate-config
```

## Canonical ARC tables

- `arc_player_weeks`: one row per player-week including weekly positional finish and spike/dud flags.
- `arc_player_seasons`: one row per player-season including games played, season points, ppg, and seasonal positional finish.
- `arc_cohort_baselines`: cohort-level baselines by `position + career_year + age_bucket`.
- `arc_career_year_baselines`: fallback baselines by `position + career_year`.
- `arc_promoted_handoff`: single promoted-lab handoff artifact with `cohort` and `career_year_fallback` baseline rows for downstream systems.

## Roadmap

- **PR2:** Build historical player-week and player-season cohort tables.
- **PR3:** Compute cohort baselines by position/career-year/age-bucket slices.
- **PR4:** Add trajectory scoring and expected-vs-actual labels.


See `docs/promoted_handoff.md` for the stable schema/contract and explicit scope boundaries.
