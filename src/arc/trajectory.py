"""Scaffold trajectory scoring module for ARC."""

import pandas as pd


def compute_trajectory_scores(player_seasons: pd.DataFrame, cohort_baselines: pd.DataFrame) -> pd.DataFrame:
    """Compute expected-vs-actual trajectory scores.

    PR1 returns an empty DataFrame placeholder.
    """

    _ = (player_seasons, cohort_baselines)
    return pd.DataFrame()


def label_trajectory(delta_vs_expected: float | None, percentile_within_cohort: float | None) -> str | None:
    """Return a trajectory label from deviation and percentile context.

    PR1 keeps labels unimplemented.
    """

    _ = (delta_vs_expected, percentile_within_cohort)
    return None
