"""Metrics and summary-table builders for ARC cohort baselines."""

from __future__ import annotations

import numpy as np
import pandas as pd

PLAYER_SEASON_KEYS = ["player_id", "season", "position"]
SMALL_SAMPLE_THRESHOLD_DEFAULT = 10


def safe_rate_mean(series: pd.Series) -> float | None:
    """Return a null-safe mean for rate-like numeric values."""

    if series.empty:
        return None

    value = series.dropna().mean()
    if pd.isna(value):
        return None
    return float(value)


def safe_numeric_summary(series: pd.Series) -> dict[str, float | None]:
    """Return mean/median/std summary statistics for a numeric series."""

    cleaned = series.dropna()
    if cleaned.empty:
        return {"mean": None, "median": None, "std": None}

    mean_value = cleaned.mean()
    median_value = cleaned.median()
    std_value = cleaned.std(ddof=1)

    return {
        "mean": None if pd.isna(mean_value) else float(mean_value),
        "median": None if pd.isna(median_value) else float(median_value),
        "std": None if pd.isna(std_value) else float(std_value),
    }


def aggregate_player_season_event_rates(player_weeks_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate weekly spike/dud counts and rates to the player-season level."""

    weeks = player_weeks_df.copy()
    valid_game = weeks["fantasy_points"].notna()
    weeks["_valid_game"] = valid_game.astype(int)
    weeks["_spike_game"] = (weeks["spike_flag"].fillna(False) & valid_game).astype(int)
    weeks["_dud_game"] = (weeks["dud_flag"].fillna(False) & valid_game).astype(int)

    grouped = weeks.groupby(PLAYER_SEASON_KEYS, dropna=False).agg(
        games_played=("_valid_game", "sum"),
        spike_weeks=("_spike_game", "sum"),
        dud_weeks=("_dud_game", "sum"),
    )

    rates = grouped.reset_index()
    denom = rates["games_played"].replace(0, np.nan)
    rates["spike_rate_player_season"] = rates["spike_weeks"] / denom
    rates["dud_rate_player_season"] = rates["dud_weeks"] / denom
    return rates


def build_player_season_event_rates(player_weeks_df: pd.DataFrame) -> pd.DataFrame:
    """Public wrapper for per-player-season spike/dud rate calculation."""

    return aggregate_player_season_event_rates(player_weeks_df)


def _prepare_season_features(
    player_seasons_df: pd.DataFrame,
    player_weeks_df: pd.DataFrame,
) -> pd.DataFrame:
    seasons = player_seasons_df.copy()
    event_rates = aggregate_player_season_event_rates(player_weeks_df)
    merged = seasons.merge(
        event_rates[PLAYER_SEASON_KEYS + ["spike_rate_player_season", "dud_rate_player_season"]],
        on=PLAYER_SEASON_KEYS,
        how="left",
    )
    return merged


def _compute_grouped_baselines(
    merged_seasons_df: pd.DataFrame,
    group_columns: list[str],
    small_sample_threshold: int,
) -> pd.DataFrame:
    enriched = merged_seasons_df.copy()
    enriched["_elite_finish_numeric"] = enriched["top_tier_finish"].astype(float)
    enriched["_starter_finish_numeric"] = enriched["starter_tier_finish"].astype(float)

    grouped = enriched.groupby(group_columns, dropna=False)
    sample_sizes = grouped.size().rename("sample_size").reset_index()
    metric_aggregates = grouped.agg(
        avg_ppg=("ppg", "mean"),
        median_ppg=("ppg", "median"),
        ppg_std=("ppg", "std"),
        avg_season_points=("season_points", "mean"),
        median_season_points=("season_points", "median"),
        avg_games_played=("games_played", "mean"),
        spike_rate=("spike_rate_player_season", safe_rate_mean),
        dud_rate=("dud_rate_player_season", safe_rate_mean),
        elite_finish_rate=("_elite_finish_numeric", safe_rate_mean),
        starter_finish_rate=("_starter_finish_numeric", safe_rate_mean),
    ).reset_index()

    baseline = sample_sizes.merge(metric_aggregates, on=group_columns, how="left")

    baseline["small_sample_threshold"] = int(small_sample_threshold)
    baseline["is_small_sample"] = baseline["sample_size"] < small_sample_threshold

    ordered_columns = (
        group_columns
        + [
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
    )
    return baseline.reindex(columns=ordered_columns)


def compute_cohort_baselines(
    player_seasons_df: pd.DataFrame,
    player_weeks_df: pd.DataFrame,
    small_sample_threshold: int = SMALL_SAMPLE_THRESHOLD_DEFAULT,
) -> pd.DataFrame:
    """Compute primary cohort baselines by position + career_year + age_bucket.

    Rows missing position/career_year are excluded. Rows with null age_bucket are
    excluded from this primary output and should be represented in fallback tables.
    """

    merged = _prepare_season_features(player_seasons_df, player_weeks_df)
    filtered = merged[
        merged["position"].notna() & merged["career_year"].notna() & merged["age_bucket"].notna()
    ]
    return _compute_grouped_baselines(
        filtered,
        group_columns=["position", "career_year", "age_bucket"],
        small_sample_threshold=small_sample_threshold,
    )


def compute_career_year_baselines(
    player_seasons_df: pd.DataFrame,
    player_weeks_df: pd.DataFrame,
    small_sample_threshold: int = SMALL_SAMPLE_THRESHOLD_DEFAULT,
) -> pd.DataFrame:
    """Compute fallback baselines by position + career_year (age bucket ignored)."""

    merged = _prepare_season_features(player_seasons_df, player_weeks_df)
    filtered = merged[merged["position"].notna() & merged["career_year"].notna()]
    return _compute_grouped_baselines(
        filtered,
        group_columns=["position", "career_year"],
        small_sample_threshold=small_sample_threshold,
    )
