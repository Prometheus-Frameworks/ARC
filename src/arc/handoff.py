"""Promoted handoff artifact builder for downstream ARC consumers."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

BASELINE_METRIC_COLUMNS = [
    "sample_size",
    "avg_ppg",
    "median_ppg",
    "ppg_std",
    "avg_season_points",
    "median_season_points",
    "avg_games_played",
    "spike_rate",
    "dud_rate",
    "elite_finish_rate",
    "starter_finish_rate",
    "is_small_sample",
    "small_sample_threshold",
]

PROMOTED_HANDOFF_COLUMNS = [
    "build_timestamp_utc",
    "arc_version",
    "baseline_level",
    "resolution_priority",
    "position",
    "career_year",
    "age_bucket",
    *BASELINE_METRIC_COLUMNS,
]

RESOLUTION_PRIORITY = {
    "cohort": 1,
    "career_year_fallback": 2,
}


def validate_promoted_handoff(promoted_handoff: pd.DataFrame) -> None:
    """Validate promoted handoff contract invariants.

    Raises:
        ValueError: If required contract rules are violated.
    """

    missing_columns = [
        column for column in PROMOTED_HANDOFF_COLUMNS if column not in promoted_handoff.columns
    ]
    if missing_columns:
        raise ValueError(
            "Promoted handoff is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    baseline_levels = set(promoted_handoff["baseline_level"].dropna().unique())
    allowed_levels = set(RESOLUTION_PRIORITY)
    invalid_levels = sorted(baseline_levels - allowed_levels)
    if invalid_levels:
        raise ValueError(
            "Promoted handoff has invalid baseline_level values: "
            + ", ".join(invalid_levels)
            + ". Allowed values: cohort, career_year_fallback."
        )

    invalid_resolution_rows = promoted_handoff[
        promoted_handoff["resolution_priority"]
        != promoted_handoff["baseline_level"].map(RESOLUTION_PRIORITY)
    ]
    if not invalid_resolution_rows.empty:
        sample = invalid_resolution_rows.iloc[0]
        raise ValueError(
            "Promoted handoff has non-canonical resolution_priority mapping for "
            f"baseline_level={sample['baseline_level']}: "
            f"expected={RESOLUTION_PRIORITY.get(sample['baseline_level'])}, "
            f"found={sample['resolution_priority']}."
        )

    cohort_rows = promoted_handoff[promoted_handoff["baseline_level"] == "cohort"]
    cohort_missing_age = cohort_rows[cohort_rows["age_bucket"].isna()]
    if not cohort_missing_age.empty:
        sample = cohort_missing_age.iloc[0]
        raise ValueError(
            "Promoted handoff cohort rows must include non-null age_bucket. "
            "Example invalid key: "
            f"position={sample['position']}, career_year={sample['career_year']}."
        )

    fallback_rows = promoted_handoff[
        promoted_handoff["baseline_level"] == "career_year_fallback"
    ]
    fallback_with_age = fallback_rows[fallback_rows["age_bucket"].notna()]
    if not fallback_with_age.empty:
        sample = fallback_with_age.iloc[0]
        raise ValueError(
            "Promoted handoff career_year_fallback rows must have null age_bucket. "
            "Example invalid key: "
            f"position={sample['position']}, career_year={sample['career_year']}, "
            f"age_bucket={sample['age_bucket']}."
        )

    duplicate_cohorts = cohort_rows.duplicated(
        subset=["position", "career_year", "age_bucket"], keep=False
    )
    if duplicate_cohorts.any():
        sample = cohort_rows.loc[duplicate_cohorts].iloc[0]
        raise ValueError(
            "Promoted handoff has duplicate cohort rows for key "
            f"(position, career_year, age_bucket)=({sample['position']}, "
            f"{sample['career_year']}, {sample['age_bucket']})."
        )

    duplicate_fallbacks = fallback_rows.duplicated(
        subset=["position", "career_year"], keep=False
    )
    if duplicate_fallbacks.any():
        sample = fallback_rows.loc[duplicate_fallbacks].iloc[0]
        raise ValueError(
            "Promoted handoff has duplicate career_year_fallback rows for key "
            f"(position, career_year)=({sample['position']}, {sample['career_year']})."
        )


def utc_timestamp_now() -> str:
    """Return an ISO-8601 UTC timestamp string."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_promoted_handoff(
    cohort_baselines: pd.DataFrame,
    career_year_baselines: pd.DataFrame,
    *,
    arc_version: str,
    build_timestamp_utc: str | None = None,
) -> pd.DataFrame:
    """Build the single promoted handoff table for downstream systems.

    The output is intentionally simple and truthful:
    - `cohort` rows: position + career_year + age_bucket baselines.
    - `career_year_fallback` rows: position + career_year baselines with age_bucket unset.
    """

    timestamp = build_timestamp_utc or utc_timestamp_now()

    cohort_rows = cohort_baselines.copy()
    cohort_rows["baseline_level"] = "cohort"
    cohort_rows["resolution_priority"] = RESOLUTION_PRIORITY["cohort"]

    fallback_rows = career_year_baselines.copy()
    fallback_rows["baseline_level"] = "career_year_fallback"
    fallback_rows["resolution_priority"] = RESOLUTION_PRIORITY["career_year_fallback"]
    fallback_rows["age_bucket"] = pd.NA

    promoted = pd.concat([cohort_rows, fallback_rows], ignore_index=True)
    promoted["build_timestamp_utc"] = timestamp
    promoted["arc_version"] = arc_version

    promoted = promoted.reindex(columns=PROMOTED_HANDOFF_COLUMNS)
    validate_promoted_handoff(promoted)
    return promoted


def resolve_promoted_baseline(
    promoted_handoff: pd.DataFrame,
    *,
    position: str,
    career_year: int,
    age_bucket: str | None,
) -> pd.Series:
    """Resolve the deterministic best baseline row from promoted handoff inputs.

    Selection order:
    1. Prefer `cohort` row matching position + career_year + age_bucket.
    2. Fall back to `career_year_fallback` row matching position + career_year.

    Raises:
        KeyError: If no matching cohort or fallback baseline exists.
    """

    scoped = promoted_handoff[
        (promoted_handoff["position"] == position)
        & (promoted_handoff["career_year"] == career_year)
    ]

    cohort_match = scoped[
        (scoped["baseline_level"] == "cohort") & (scoped["age_bucket"] == age_bucket)
    ]
    if not cohort_match.empty:
        return cohort_match.sort_values("resolution_priority", ascending=True).iloc[0]

    fallback_match = scoped[scoped["baseline_level"] == "career_year_fallback"]
    if not fallback_match.empty:
        return fallback_match.sort_values("resolution_priority", ascending=True).iloc[0]

    raise KeyError(
        "No promoted baseline found for "
        f"position={position}, career_year={career_year}, age_bucket={age_bucket}."
    )
