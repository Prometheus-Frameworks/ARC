from pathlib import Path

import pandas as pd
import pytest
from typer.testing import CliRunner

from arc.cli import app
from arc.handoff import (
    PROMOTED_HANDOFF_COLUMNS,
    build_promoted_handoff,
    resolve_promoted_baseline,
    validate_promoted_handoff,
)


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
    assert handoff["resolution_priority"].tolist() == [1, 2]
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


def test_resolve_promoted_baseline_prefers_cohort_then_fallback() -> None:
    promoted = pd.DataFrame(
        {
            "baseline_level": ["cohort", "career_year_fallback"],
            "resolution_priority": [1, 2],
            "position": ["WR", "WR"],
            "career_year": [2, 2],
            "age_bucket": ["24-25", pd.NA],
            "sample_size": [5, 30],
        }
    )

    cohort_row = resolve_promoted_baseline(
        promoted,
        position="WR",
        career_year=2,
        age_bucket="24-25",
    )
    assert cohort_row["baseline_level"] == "cohort"
    assert cohort_row["sample_size"] == 5

    fallback_row = resolve_promoted_baseline(
        promoted,
        position="WR",
        career_year=2,
        age_bucket="26-27",
    )
    assert fallback_row["baseline_level"] == "career_year_fallback"
    assert fallback_row["sample_size"] == 30


def test_resolve_promoted_baseline_raises_when_no_matching_rows() -> None:
    promoted = pd.DataFrame(
        {
            "baseline_level": ["cohort"],
            "resolution_priority": [1],
            "position": ["WR"],
            "career_year": [2],
            "age_bucket": ["24-25"],
            "sample_size": [5],
        }
    )

    with pytest.raises(KeyError, match="No promoted baseline found"):
        resolve_promoted_baseline(
            promoted,
            position="RB",
            career_year=2,
            age_bucket="24-25",
        )


def test_validate_promoted_handoff_passes_for_well_formed_artifact() -> None:
    promoted = pd.DataFrame(
        {
            "build_timestamp_utc": ["2026-03-24T00:00:00+00:00", "2026-03-24T00:00:00+00:00"],
            "arc_version": ["0.1.0", "0.1.0"],
            "baseline_level": ["cohort", "career_year_fallback"],
            "resolution_priority": [1, 2],
            "position": ["WR", "WR"],
            "career_year": [2, 2],
            "age_bucket": ["24-25", pd.NA],
            "sample_size": [5, 30],
            "avg_ppg": [13.2, 12.5],
            "median_ppg": [12.8, 12.3],
            "ppg_std": [1.1, 1.8],
            "avg_season_points": [211.0, 198.0],
            "median_season_points": [209.0, 196.0],
            "avg_games_played": [16.0, 15.3],
            "spike_rate": [0.20, 0.18],
            "dud_rate": [0.11, 0.12],
            "elite_finish_rate": [0.4, 0.33],
            "starter_finish_rate": [0.6, 0.67],
            "is_small_sample": [True, False],
            "small_sample_threshold": [10, 10],
        }
    )

    validate_promoted_handoff(promoted)


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("baseline_level", "bad_level", "invalid baseline_level values"),
        ("resolution_priority", 999, "non-canonical resolution_priority mapping"),
    ],
)
def test_validate_promoted_handoff_rejects_invalid_levels_and_resolution_priority(
    field: str,
    value: object,
    expected_error: str,
) -> None:
    promoted = pd.DataFrame(
        {
            "build_timestamp_utc": ["2026-03-24T00:00:00+00:00", "2026-03-24T00:00:00+00:00"],
            "arc_version": ["0.1.0", "0.1.0"],
            "baseline_level": ["cohort", "career_year_fallback"],
            "resolution_priority": [1, 2],
            "position": ["WR", "WR"],
            "career_year": [2, 2],
            "age_bucket": ["24-25", pd.NA],
            "sample_size": [5, 30],
            "avg_ppg": [13.2, 12.5],
            "median_ppg": [12.8, 12.3],
            "ppg_std": [1.1, 1.8],
            "avg_season_points": [211.0, 198.0],
            "median_season_points": [209.0, 196.0],
            "avg_games_played": [16.0, 15.3],
            "spike_rate": [0.20, 0.18],
            "dud_rate": [0.11, 0.12],
            "elite_finish_rate": [0.4, 0.33],
            "starter_finish_rate": [0.6, 0.67],
            "is_small_sample": [True, False],
            "small_sample_threshold": [10, 10],
        }
    )
    promoted.loc[0, field] = value

    with pytest.raises(ValueError, match=expected_error):
        validate_promoted_handoff(promoted)


def test_validate_promoted_handoff_rejects_duplicate_cohort_keys() -> None:
    promoted = pd.DataFrame(
        {
            "build_timestamp_utc": ["2026-03-24T00:00:00+00:00"] * 3,
            "arc_version": ["0.1.0"] * 3,
            "baseline_level": ["cohort", "cohort", "career_year_fallback"],
            "resolution_priority": [1, 1, 2],
            "position": ["WR", "WR", "WR"],
            "career_year": [2, 2, 2],
            "age_bucket": ["24-25", "24-25", pd.NA],
            "sample_size": [5, 6, 30],
            "avg_ppg": [13.2, 13.3, 12.5],
            "median_ppg": [12.8, 13.0, 12.3],
            "ppg_std": [1.1, 1.0, 1.8],
            "avg_season_points": [211.0, 213.0, 198.0],
            "median_season_points": [209.0, 211.0, 196.0],
            "avg_games_played": [16.0, 16.0, 15.3],
            "spike_rate": [0.20, 0.21, 0.18],
            "dud_rate": [0.11, 0.10, 0.12],
            "elite_finish_rate": [0.4, 0.41, 0.33],
            "starter_finish_rate": [0.6, 0.61, 0.67],
            "is_small_sample": [True, True, False],
            "small_sample_threshold": [10, 10, 10],
        }
    )

    with pytest.raises(ValueError, match="duplicate cohort rows"):
        validate_promoted_handoff(promoted)


def test_validate_promoted_handoff_rejects_invalid_age_bucket_presence() -> None:
    promoted = pd.DataFrame(
        {
            "build_timestamp_utc": ["2026-03-24T00:00:00+00:00", "2026-03-24T00:00:00+00:00"],
            "arc_version": ["0.1.0", "0.1.0"],
            "baseline_level": ["cohort", "career_year_fallback"],
            "resolution_priority": [1, 2],
            "position": ["WR", "WR"],
            "career_year": [2, 2],
            "age_bucket": [pd.NA, "24-25"],
            "sample_size": [5, 30],
            "avg_ppg": [13.2, 12.5],
            "median_ppg": [12.8, 12.3],
            "ppg_std": [1.1, 1.8],
            "avg_season_points": [211.0, 198.0],
            "median_season_points": [209.0, 196.0],
            "avg_games_played": [16.0, 15.3],
            "spike_rate": [0.20, 0.18],
            "dud_rate": [0.11, 0.12],
            "elite_finish_rate": [0.4, 0.33],
            "starter_finish_rate": [0.6, 0.67],
            "is_small_sample": [True, False],
            "small_sample_threshold": [10, 10],
        }
    )

    with pytest.raises(ValueError, match="cohort rows must include non-null age_bucket"):
        validate_promoted_handoff(promoted)


def test_validate_promoted_handoff_cli_fails_for_malformed_artifact(tmp_path: Path) -> None:
    runner = CliRunner()
    invalid = pd.DataFrame(
        {
            "build_timestamp_utc": ["2026-03-24T00:00:00+00:00"],
            "arc_version": ["0.1.0"],
            "baseline_level": ["career_year_fallback"],
            "resolution_priority": [2],
            "position": ["WR"],
            "career_year": [2],
            "age_bucket": ["24-25"],
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
    input_path = tmp_path / "arc_promoted_handoff.csv"
    invalid.to_csv(input_path, index=False)

    result = runner.invoke(app, ["validate-promoted-handoff", "--input-path", str(input_path)])

    assert result.exit_code != 0
    assert "career_year_fallback rows must have null" in result.output
    assert "age_bucket" in result.output
