import pandas as pd

from arc.cohort_builder import (
    assign_age_buckets,
    assign_career_years,
    build_player_seasons,
    build_player_weeks,
)


def test_age_bucket_assignment() -> None:
    df = pd.DataFrame({"age": [21.9, 22.0, 25.0, 31.2, None]})
    result = assign_age_buckets(df)

    assert result["age_bucket"].tolist()[:4] == ["<22", "22-23", "24-25", "30+"]
    assert pd.isna(result["age_bucket"].tolist()[4])


def test_career_year_assignment() -> None:
    df = pd.DataFrame(
        {
            "player_id": ["a", "a", "a", "b"],
            "position": ["WR", "WR", "WR", "WR"],
            "season": [2020, 2022, 2021, 2022],
        }
    )

    result = assign_career_years(df).sort_values(["player_id", "season"])
    assert result["career_year"].tolist() == [1, 2, 3, 1]


def test_weekly_finish_ranking_and_flags() -> None:
    df = pd.DataFrame(
        {
            "player_id": ["q1", "q2", "q3", "q4"],
            "player_name": ["Q1", "Q2", "Q3", "Q4"],
            "season": [2023, 2023, 2023, 2023],
            "week": [1, 1, 1, 1],
            "position": ["QB", "QB", "QB", "QB"],
            "team": ["A", "B", "C", "D"],
            "age": [24, 25, 23, 29],
            "fantasy_points": [30.0, 22.0, 22.0, 5.0],
        }
    )

    result = build_player_weeks(df)
    assert result["weekly_pos_finish"].tolist() == [1, 2, 2, 4]
    assert result["spike_flag"].tolist() == [True, True, True, True]
    assert result["dud_flag"].tolist() == [False, False, False, False]


def test_season_aggregation() -> None:
    weeks = pd.DataFrame(
        {
            "player_id": ["r1", "r1", "r2", "r2"],
            "player_name": ["R1", "R1", "R2", "R2"],
            "season": [2023, 2023, 2023, 2023],
            "week": [1, 2, 1, 2],
            "position": ["RB", "RB", "RB", "RB"],
            "team": ["A", "A", "B", "B"],
            "age": [24, 24, 27, 27],
            "age_bucket": ["24-25", "24-25", "26-27", "26-27"],
            "career_year": [1, 1, 2, 2],
            "fantasy_points": [10.0, 15.0, 8.0, None],
            "weekly_pos_finish": [1, 1, 2, None],
            "spike_flag": [True, True, True, False],
            "dud_flag": [False, False, False, False],
        }
    )

    seasons = build_player_seasons(weeks).sort_values("player_id").reset_index(drop=True)

    assert seasons.loc[0, "games_played"] == 2
    assert seasons.loc[0, "season_points"] == 25.0
    assert seasons.loc[0, "ppg"] == 12.5
    assert seasons.loc[0, "positional_finish"] == 1
    assert seasons.loc[0, "top_tier_finish"] == True

    assert seasons.loc[1, "games_played"] == 1
    assert seasons.loc[1, "season_points"] == 8.0
    assert seasons.loc[1, "ppg"] == 8.0
    assert seasons.loc[1, "positional_finish"] == 2
    assert seasons.loc[1, "starter_tier_finish"] == True
