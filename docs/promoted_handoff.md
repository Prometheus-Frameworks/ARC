# ARC promoted handoff contract

ARC now publishes one downstream handoff artifact:

- **Canonical artifact path:** `outputs/promoted/arc_promoted_handoff.csv`
- **Build command:** `python -m arc.cli build-promoted-handoff`

This file is the smallest honest handoff ARC can guarantee today. It is a deterministic export of already-computed historical baselines. ARC does **not** add forecasting or synthetic confidence beyond these cohort summaries.

## Schema (stable)

| Column | Type | Guarantee |
| --- | --- | --- |
| `build_timestamp_utc` | string (ISO-8601 UTC) | Build timestamp shared by all rows in one run. |
| `arc_version` | string | ARC package version used to produce the file. |
| `baseline_level` | string | `cohort` or `career_year_fallback`. |
| `resolution_priority` | int | Canonical selection order (`1=cohort`, `2=career_year_fallback`). |
| `position` | string | Offensive position key (RB/WR/TE/QB). |
| `career_year` | int | Career year bucket key. |
| `age_bucket` | string or null | Present for `cohort`; null for `career_year_fallback`. |
| `sample_size` | int | Number of player-seasons used in that baseline row. |
| `avg_ppg` | float or null | Mean player-season PPG. |
| `median_ppg` | float or null | Median player-season PPG. |
| `ppg_std` | float or null | Sample standard deviation of PPG. |
| `avg_season_points` | float or null | Mean season points. |
| `median_season_points` | float or null | Median season points. |
| `avg_games_played` | float or null | Mean games played. |
| `spike_rate` | float or null | Mean player-season spike-week rate. |
| `dud_rate` | float or null | Mean player-season dud-week rate. |
| `elite_finish_rate` | float or null | Share of seasons meeting top-tier finish cutoffs. |
| `starter_finish_rate` | float or null | Share of seasons meeting starter-tier cutoffs. |
| `is_small_sample` | bool | Explicit low-sample warning for this row. |
| `small_sample_threshold` | int | Threshold used to set `is_small_sample`. |

## Consumer expectations

Downstream consumers should trust this file as **historical baseline context** only.

Canonical row resolution rule for one player context (`position`, `career_year`, optional `age_bucket`):

1. Filter to rows matching `position` + `career_year`.
2. If any `cohort` row matches the input `age_bucket`, choose that row (`resolution_priority=1`).
3. Otherwise choose the `career_year_fallback` row (`resolution_priority=2`).
4. Keep `is_small_sample` as-is from the selected row; do not treat fallback as a confidence upgrade.

Concrete example:

- Input context: `position=WR`, `career_year=2`, `age_bucket=26-27`
- If no `cohort` row exists for `26-27`, select the `career_year_fallback` row for `WR + 2`.
- If that fallback row has `is_small_sample=true`, it remains explicitly small-sample.

## Explicitly out of scope (today)

ARC promoted handoff does **not** currently provide:

- trajectory score outputs (module still scaffold/placeholder)
- forward-looking projections
- confidence calibration beyond sample-size transparency
- service/API endpoint guarantees
