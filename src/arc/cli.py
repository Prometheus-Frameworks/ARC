"""CLI entrypoint for ARC cohort build and config commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from arc import __version__
from arc.cohort_builder import (
    build_player_seasons,
    build_player_weeks,
    load_weekly_source,
    normalize_weekly_columns,
)
from arc.config import (
    AGE_BUCKETS,
    ELITE_SEASON_FINISH_CUTOFFS,
    STARTER_SEASON_FINISH_CUTOFFS,
    SUPPORTED_POSITIONS,
    WEEKLY_DUD_FINISH_THRESHOLDS,
    WEEKLY_SPIKE_FINISH_THRESHOLDS,
)
from arc.exports import export_csv, export_parquet

DEFAULT_INPUT_PATH = Path("data/raw/player_weekly_history.csv")
DEFAULT_OUTPUT_DIR = Path("outputs/cohort_tables")

app = typer.Typer(help="ARC command line interface.")


@app.command("info")
def info() -> None:
    """Print project and stage information."""

    typer.echo("ARC (Age and Role Curves)")
    typer.echo("Stage: PR2 cohort pipeline")
    typer.echo(f"Version: {__version__}")
    typer.echo("Purpose: Historical fantasy football cohort intelligence engine")


@app.command("validate-config")
def validate_config() -> None:
    """Print core config values to confirm scaffold wiring."""

    payload = {
        "positions": list(SUPPORTED_POSITIONS),
        "age_buckets": list(AGE_BUCKETS),
        "weekly_spike_finish_thresholds": WEEKLY_SPIKE_FINISH_THRESHOLDS,
        "weekly_dud_finish_thresholds": WEEKLY_DUD_FINISH_THRESHOLDS,
        "elite_season_finish_cutoffs": ELITE_SEASON_FINISH_CUTOFFS,
        "starter_season_finish_cutoffs": STARTER_SEASON_FINISH_CUTOFFS,
    }
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@app.command("build-cohorts")
def build_cohorts(
    input: Path = typer.Option(DEFAULT_INPUT_PATH, "--input", help="Raw weekly input file (.csv/.parquet)."),
    output_dir: Path = typer.Option(DEFAULT_OUTPUT_DIR, "--output-dir", help="Directory for cohort table outputs."),
) -> None:
    """Build canonical ARC player-week and player-season cohort tables."""

    try:
        raw = load_weekly_source(input)
    except FileNotFoundError as exc:
        raise typer.BadParameter(
            f"{exc}. Place the raw file at {DEFAULT_INPUT_PATH} or pass --input."
        ) from exc

    normalized = normalize_weekly_columns(raw)
    player_weeks = build_player_weeks(normalized)
    player_seasons = build_player_seasons(player_weeks)

    weeks_csv = output_dir / "arc_player_weeks.csv"
    seasons_csv = output_dir / "arc_player_seasons.csv"
    export_csv(player_weeks, weeks_csv)
    export_csv(player_seasons, seasons_csv)

    parquet_written: list[str] = []
    for df, output in (
        (player_weeks, output_dir / "arc_player_weeks.parquet"),
        (player_seasons, output_dir / "arc_player_seasons.parquet"),
    ):
        try:
            export_parquet(df, output)
            parquet_written.append(str(output))
        except RuntimeError:
            continue

    typer.echo("Built ARC cohort tables")
    typer.echo(f"Rows: weeks={len(player_weeks):,}, seasons={len(player_seasons):,}")
    typer.echo(f"CSV outputs: {weeks_csv}, {seasons_csv}")
    if parquet_written:
        typer.echo("Parquet outputs: " + ", ".join(parquet_written))
    else:
        typer.echo("Parquet outputs skipped (install pyarrow to enable)")


if __name__ == "__main__":
    app()
