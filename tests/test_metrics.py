import pandas as pd

from arc.metrics import (
    build_player_season_event_rates,
    compute_career_year_baselines,
    compute_cohort_baselines,
)


def _sample_player_weeks() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "player_id": ["p1", "p1", "p2", "p2", "p3", "p3"],
            "season": [2023, 2023, 2023, 2023, 2023, 2023],
            "position": ["WR", "WR", "WR", "WR", "RB", "RB"],
            "fantasy_points": [10.0, 12.0, 8.0, 7.0, 15.0, None],
            "spike_flag": [True, False, False, True, True, False],
            "dud_flag": [False, True, True, False, False, False],
        }
    )


def _sample_player_seasons() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "player_id": ["p1", "p2", "p3", "p4"],
            "player_name": ["P1", "P2", "P3", "P4"],
            "season": [2023, 2023, 2023, 2023],
            "position": ["WR", "WR", "RB", "WR"],
            "age_bucket": ["24-25", "24-25", "22-23", None],
            "career_year": [2, 2, 1, 2],
            "games_played": [2, 2, 1, 1],
            "season_points": [22.0, 15.0, 15.0, 5.0],
            "ppg": [11.0, 7.5, 15.0, 5.0],
            "top_tier_finish": [True, False, True, False],
            "starter_tier_finish": [True, True, True, False],
        }
    )


def test_player_season_event_rate_aggregation() -> None:
    rates = build_player_season_event_rates(_sample_player_weeks()).sort_values(
        ["player_id"]
    )

    p1 = rates[rates["player_id"] == "p1"].iloc[0]
    p3 = rates[rates["player_id"] == "p3"].iloc[0]

    assert p1["games_played"] == 2
    assert p1["spike_weeks"] == 1
    assert p1["dud_weeks"] == 1
    assert p1["spike_rate_player_season"] == 0.5
    assert p1["dud_rate_player_season"] == 0.5

    assert p3["games_played"] == 1
    assert p3["spike_rate_player_season"] == 1.0
    assert p3["dud_rate_player_season"] == 0.0


def test_compute_cohort_baselines_excludes_null_age_bucket_and_flags_small_sample() -> None:
    baselines = compute_cohort_baselines(
        _sample_player_seasons(),
        _sample_player_weeks(),
        small_sample_threshold=3,
    )

    assert set(baselines["age_bucket"]) == {"24-25", "22-23"}

    wr_row = baselines[
        (baselines["position"] == "WR")
        & (baselines["career_year"] == 2)
        & (baselines["age_bucket"] == "24-25")
    ].iloc[0]

    assert wr_row["sample_size"] == 2
    assert wr_row["avg_ppg"] == 9.25
    assert wr_row["median_ppg"] == 9.25
    assert wr_row["spike_rate"] == 0.5
    assert wr_row["dud_rate"] == 0.5
    assert wr_row["elite_finish_rate"] == 0.5
    assert wr_row["starter_finish_rate"] == 1.0
    assert bool(wr_row["is_small_sample"]) is True
    assert wr_row["small_sample_threshold"] == 3


def test_compute_career_year_baselines_includes_null_age_bucket_rows() -> None:
    baselines = compute_career_year_baselines(
        _sample_player_seasons(),
        _sample_player_weeks(),
        small_sample_threshold=2,
    )

    wr_row = baselines[
        (baselines["position"] == "WR") & (baselines["career_year"] == 2)
    ].iloc[0]

    assert wr_row["sample_size"] == 3
    assert round(float(wr_row["avg_ppg"]), 4) == round((11.0 + 7.5 + 5.0) / 3, 4)
    assert bool(wr_row["is_small_sample"]) is False
    assert wr_row["small_sample_threshold"] == 2
