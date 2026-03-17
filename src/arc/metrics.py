"""Scaffold metrics module for cohort baseline calculations."""

import pandas as pd


def compute_cohort_baselines(player_seasons: pd.DataFrame, player_weeks: pd.DataFrame) -> pd.DataFrame:
    """Compute cohort baseline table from canonical season/week inputs.

    PR1 intentionally leaves implementation minimal.
    """

    _ = (player_seasons, player_weeks)
    return pd.DataFrame()


def calculate_spike_rate(player_weeks: pd.DataFrame) -> float | None:
    """Calculate spike-week rate from `arc_player_weeks` rows."""

    _ = player_weeks
    return None


def calculate_dud_rate(player_weeks: pd.DataFrame) -> float | None:
    """Calculate dud-week rate from `arc_player_weeks` rows."""

    _ = player_weeks
    return None
