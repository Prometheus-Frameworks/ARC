from pathlib import Path

import pandas as pd
from typer.testing import CliRunner

from arc.cli import app
from arc.handoff import PROMOTED_HANDOFF_COLUMNS, build_promoted_handoff


def test_build_promoted_handoff_includes_cohort_and_fallback_rows() -> None:
    cohort = pd.DataFrame(
        {
            "position": ["WR"],
            "career_year": [2],
            "age_bucket": ["24-25"],
            "sample_size": [5],
            "avg_ppg": [13.2],
            "median_ppg": [12.8],
            "ppg_std": [1.1],
            "avg_season_points": [211.0],
            "median_season_points": [209.0],
            "avg_games_played": [16.0],
            "spike_rate": [0.20],
            "dud_rate": [0.11],
            "elite_finish_rate": [0.4],
            "starter_finish_rate": [0.6],
            "is_small_sample": [True],
            "small_sample_threshold": [10],
        }
    )
    fallback = pd.DataFrame(
        {
            "position": ["WR"],
            "career_year": [2],
            "sample_size": [30],
            "avg_ppg": [12.5],
            "median_ppg": [12.3],
            "ppg_std": [1.8],
            "avg_season_points": [198.0],
            "median_season_points": [196.0],
            "avg_games_played": [15.3],
            "spike_rate": [0.18],
            "dud_rate": [0.12],
            "elite_finish_rate": [0.33],
            "starter_finish_rate": [0.67],
            "is_small_sample": [False],
            "small_sample_threshold": [10],
        }
    )

    handoff = build_promoted_handoff(
        cohort,
        fallback,
        arc_version="0.1.0",
        build_timestamp_utc="2026-03-24T00:00:00+00:00",
    )

    assert list(handoff.columns) == PROMOTED_HANDOFF_COLUMNS
    assert handoff["baseline_level"].tolist() == ["cohort", "career_year_fallback"]
    assert pd.isna(handoff.loc[1, "age_bucket"])
    assert handoff["is_small_sample"].tolist() == [True, False]


def test_build_promoted_handoff_cli_writes_canonical_output(tmp_path: Path) -> None:
    runner = CliRunner()

    cohort = pd.DataFrame(
        {
            "position": ["WR"],
            "career_year": [2],
            "age_bucket": ["24-25"],
            "sample_size": [5],
            "avg_ppg": [13.2],
            "median_ppg": [12.8],
            "ppg_std": [1.1],
            "avg_season_points": [211.0],
            "median_season_points": [209.0],
            "avg_games_played": [16.0],
            "spike_rate": [0.20],
            "dud_rate": [0.11],
            "elite_finish_rate": [0.4],
            "starter_finish_rate": [0.6],
            "is_small_sample": [True],
            "small_sample_threshold": [10],
        }
    )
    fallback = pd.DataFrame(
        {
            "position": ["WR"],
            "career_year": [2],
            "sample_size": [30],
            "avg_ppg": [12.5],
            "median_ppg": [12.3],
            "ppg_std": [1.8],
            "avg_season_points": [198.0],
            "median_season_points": [196.0],
            "avg_games_played": [15.3],
            "spike_rate": [0.18],
            "dud_rate": [0.12],
            "elite_finish_rate": [0.33],
            "starter_finish_rate": [0.67],
            "is_small_sample": [False],
            "small_sample_threshold": [10],
        }
    )

    cohort_path = tmp_path / "arc_cohort_baselines.csv"
    fallback_path = tmp_path / "arc_career_year_baselines.csv"
    output_path = tmp_path / "arc_promoted_handoff.csv"

    cohort.to_csv(cohort_path, index=False)
    fallback.to_csv(fallback_path, index=False)

    result = runner.invoke(
        app,
        [
            "build-promoted-handoff",
            "--cohort-baselines-path",
            str(cohort_path),
            "--career-year-baselines-path",
            str(fallback_path),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()

    exported = pd.read_csv(output_path)
    assert list(exported.columns) == PROMOTED_HANDOFF_COLUMNS
    assert set(exported["baseline_level"]) == {"cohort", "career_year_fallback"}
