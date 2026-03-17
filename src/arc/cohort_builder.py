"""Scaffold functions for constructing ARC canonical player tables."""

import pandas as pd


def build_player_seasons(*args, **kwargs) -> pd.DataFrame:
    """Build the canonical `arc_player_seasons` table.

    PR1 returns an empty DataFrame with expected columns as a safe placeholder.
    """

    return pd.DataFrame(
        columns=[
            "player_id",
            "player_name",
            "season",
            "position",
            "team",
            "age",
            "age_bucket",
            "career_year",
            "games_played",
            "ppg",
            "season_points",
            "positional_finish",
            "top_tier_finish",
            "starter_tier_finish",
        ]
    )


def build_player_weeks(*args, **kwargs) -> pd.DataFrame:
    """Build the canonical `arc_player_weeks` table.

    PR1 returns an empty DataFrame with expected columns as a safe placeholder.
    """

    return pd.DataFrame(
        columns=[
            "player_id",
            "player_name",
            "season",
            "week",
            "position",
            "fantasy_points",
            "weekly_pos_finish",
            "spike_flag",
            "dud_flag",
        ]
    )
