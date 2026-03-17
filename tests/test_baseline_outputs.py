from pathlib import Path

import pandas as pd
from typer.testing import CliRunner

from arc.cli import app


def test_build_baselines_cli_writes_outputs(tmp_path: Path) -> None:
    runner = CliRunner()

    player_weeks = pd.DataFrame(
        {
            "player_id": ["a", "a", "b", "b"],
            "season": [2023, 2023, 2023, 2023],
            "position": ["WR", "WR", "WR", "WR"],
            "fantasy_points": [12.0, 8.0, 10.0, 9.0],
            "spike_flag": [True, False, True, False],
            "dud_flag": [False, True, False, True],
        }
    )
    player_seasons = pd.DataFrame(
        {
            "player_id": ["a", "b"],
            "player_name": ["A", "B"],
            "season": [2023, 2023],
            "position": ["WR", "WR"],
            "age_bucket": ["24-25", "24-25"],
            "career_year": [2, 2],
            "games_played": [2, 2],
            "season_points": [20.0, 19.0],
            "ppg": [10.0, 9.5],
            "top_tier_finish": [True, False],
            "starter_tier_finish": [True, True],
        }
    )

    weeks_path = tmp_path / "arc_player_weeks.csv"
    seasons_path = tmp_path / "arc_player_seasons.csv"
    out_dir = tmp_path / "summary"
    player_weeks.to_csv(weeks_path, index=False)
    player_seasons.to_csv(seasons_path, index=False)

    result = runner.invoke(
        app,
        [
            "build-baselines",
            "--player-weeks-path",
            str(weeks_path),
            "--player-seasons-path",
            str(seasons_path),
            "--output-dir",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0
    assert (out_dir / "arc_cohort_baselines.csv").exists()
    assert (out_dir / "arc_career_year_baselines.csv").exists()
