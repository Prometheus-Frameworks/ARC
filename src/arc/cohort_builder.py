"""Pipeline builders for ARC historical player-week and player-season tables."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from arc.breakout_defs import classify_season_finish, is_dud_week, is_spike_week
from arc.config import AGE_BUCKETS

REQUIRED_WEEKLY_COLUMNS = {
    "player_id",
    "player_name",
    "season",
    "week",
    "position",
    "team",
    "fantasy_points",
}

COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "player_id": ("player_id", "playerid", "gsis_id"),
    "player_name": ("player_name", "name", "full_name"),
    "season": ("season", "year"),
    "week": ("week",),
    "position": ("position", "pos"),
    "team": ("team", "recent_team"),
    "fantasy_points": ("fantasy_points", "fantasy_pts", "points"),
    "age": ("age",),
    "birth_date": ("birth_date", "dob", "date_of_birth"),
}

WEEK_OUTPUT_COLUMNS = [
    "player_id",
    "player_name",
    "season",
    "week",
    "position",
    "team",
    "age",
    "age_bucket",
    "career_year",
    "fantasy_points",
    "weekly_pos_finish",
    "spike_flag",
    "dud_flag",
]

SEASON_OUTPUT_COLUMNS = [
    "player_id",
    "player_name",
    "season",
    "position",
    "team",
    "age",
    "age_bucket",
    "career_year",
    "games_played",
    "season_points",
    "ppg",
    "positional_finish",
    "top_tier_finish",
    "starter_tier_finish",
]


def load_weekly_source(path: str | Path) -> pd.DataFrame:
    """Load historical weekly data from a CSV or Parquet file."""

    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(f"Input file not found: {source_path}")

    if source_path.suffix.lower() == ".csv":
        return pd.read_csv(source_path)
    if source_path.suffix.lower() == ".parquet":
        return pd.read_parquet(source_path)

    raise ValueError(
        f"Unsupported input format '{source_path.suffix}'. Use .csv or .parquet."
    )


def normalize_weekly_columns(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Normalize common source aliases to ARC canonical weekly columns."""

    normalized = raw_df.copy()
    normalized.columns = [str(col).strip().lower() for col in normalized.columns]

    rename_map: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized.columns:
                rename_map[alias] = canonical
                break

    normalized = normalized.rename(columns=rename_map)

    missing = sorted(REQUIRED_WEEKLY_COLUMNS - set(normalized.columns))
    if missing:
        raise ValueError(
            "Missing required columns after normalization: " + ", ".join(missing)
        )

    normalized["season"] = pd.to_numeric(normalized["season"], errors="coerce").astype("Int64")
    normalized["week"] = pd.to_numeric(normalized["week"], errors="coerce").astype("Int64")
    normalized["fantasy_points"] = pd.to_numeric(
        normalized["fantasy_points"], errors="coerce"
    )

    if "age" in normalized.columns:
        normalized["age"] = pd.to_numeric(normalized["age"], errors="coerce")
    elif "birth_date" in normalized.columns:
        birth_date = pd.to_datetime(normalized["birth_date"], errors="coerce")
        season_anchor = pd.to_datetime(
            normalized["season"].astype(str) + "-09-01", errors="coerce"
        )
        normalized["age"] = (
            (season_anchor - birth_date).dt.days / 365.25
        ).round(1)
    else:
        normalized["age"] = np.nan

    return normalized


def _parse_age_bucket_label(bucket_label: str) -> tuple[float | None, float | None]:
    if bucket_label.startswith("<"):
        return (None, float(bucket_label[1:]))
    if bucket_label.endswith("+"):
        return (float(bucket_label[:-1]), None)
    low, high = bucket_label.split("-")
    return (float(low), float(high))


def assign_age_buckets(df: pd.DataFrame, age_column: str = "age") -> pd.DataFrame:
    """Assign configured age buckets while preserving null age values."""

    enriched = df.copy()

    def classify_age(age_value: float | None) -> str | None:
        if pd.isna(age_value):
            return None
        for bucket in AGE_BUCKETS:
            low, high = _parse_age_bucket_label(bucket)
            if low is None and age_value < high:
                return bucket
            if high is None and age_value >= low:
                return bucket
            if low is not None and high is not None and low <= age_value <= high:
                return bucket
        return None

    enriched["age_bucket"] = enriched[age_column].apply(classify_age)
    return enriched


def assign_career_years(df: pd.DataFrame) -> pd.DataFrame:
    """Assign career year per player-position based on first observed season."""

    enriched = df.copy()
    first_season = (
        enriched.groupby(["player_id", "position"], dropna=False)["season"]
        .transform("min")
        .astype("Int64")
    )
    enriched["career_year"] = (enriched["season"] - first_season + 1).astype("Int64")
    return enriched


def build_player_weeks(normalized_weekly_df: pd.DataFrame) -> pd.DataFrame:
    """Build ARC canonical player-week table from normalized weekly source data."""

    df = normalized_weekly_df.copy()
    df = assign_career_years(df)
    df = assign_age_buckets(df)

    valid_points = df["fantasy_points"].notna()
    df.loc[valid_points, "weekly_pos_finish"] = (
        df.loc[valid_points]
        .groupby(["season", "week", "position"], dropna=False)["fantasy_points"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    df.loc[~valid_points, "weekly_pos_finish"] = pd.NA
    df["weekly_pos_finish"] = df["weekly_pos_finish"].astype("Int64")

    df["spike_flag"] = df.apply(
        lambda row: is_spike_week(row["position"], row["weekly_pos_finish"]), axis=1
    )
    df["dud_flag"] = df.apply(
        lambda row: is_dud_week(row["position"], row["weekly_pos_finish"]), axis=1
    )

    return df.reindex(columns=WEEK_OUTPUT_COLUMNS)


def build_player_seasons(player_weeks_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate ARC canonical player-season table from ARC player-week rows."""

    grouped = player_weeks_df.groupby(
        ["player_id", "player_name", "season", "position"], dropna=False
    )

    seasons = grouped.agg(
        team=("team", "last"),
        age=("age", "last"),
        age_bucket=("age_bucket", "last"),
        career_year=("career_year", "last"),
        games_played=("fantasy_points", lambda s: int(s.notna().sum())),
        season_points=("fantasy_points", "sum"),
    ).reset_index()

    seasons["season_points"] = seasons["season_points"].where(
        seasons["games_played"] > 0, np.nan
    )
    seasons["ppg"] = seasons["season_points"] / seasons["games_played"].replace(0, np.nan)

    valid = seasons["season_points"].notna()
    seasons.loc[valid, "positional_finish"] = (
        seasons.loc[valid]
        .groupby(["season", "position"], dropna=False)["season_points"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    seasons.loc[~valid, "positional_finish"] = pd.NA
    seasons["positional_finish"] = seasons["positional_finish"].astype("Int64")

    season_labels = seasons.apply(
        lambda row: classify_season_finish(row["position"], row["positional_finish"]),
        axis=1,
    )
    seasons["top_tier_finish"] = season_labels.eq("top_tier")
    seasons["starter_tier_finish"] = season_labels.isin(["top_tier", "starter_tier"])

    return seasons.reindex(columns=SEASON_OUTPUT_COLUMNS)
