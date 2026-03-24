"""CLI entrypoint for ARC cohort and summary table commands."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
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
from arc.handoff import build_promoted_handoff
from arc.metrics import compute_career_year_baselines, compute_cohort_baselines

DEFAULT_INPUT_PATH = Path("data/raw/player_weekly_history.csv")
DEFAULT_OUTPUT_DIR = Path("outputs/cohort_tables")
DEFAULT_SUMMARY_DIR = Path("outputs/summary_tables")
DEFAULT_PLAYER_WEEKS_PATH = DEFAULT_OUTPUT_DIR / "arc_player_weeks.csv"
DEFAULT_PLAYER_SEASONS_PATH = DEFAULT_OUTPUT_DIR / "arc_player_seasons.csv"
DEFAULT_PROMOTED_DIR = Path("outputs/promoted")
DEFAULT_COHORT_BASELINES_PATH = DEFAULT_SUMMARY_DIR / "arc_cohort_baselines.csv"
DEFAULT_CAREER_BASELINES_PATH = DEFAULT_SUMMARY_DIR / "arc_career_year_baselines.csv"
DEFAULT_PROMOTED_HANDOFF_PATH = DEFAULT_PROMOTED_DIR / "arc_promoted_handoff.csv"

app = typer.Typer(help="ARC command line interface.")


def _read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported input format '{path.suffix}'. Use .csv or .parquet.")


@app.command("info")
def info() -> None:
    """Print project and stage information."""

    typer.echo("ARC (Age and Role Curves)")
    typer.echo("Stage: PR3 baseline summaries")
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


@app.command("build-baselines")
def build_baselines(
    player_weeks_path: Path = typer.Option(
        DEFAULT_PLAYER_WEEKS_PATH,
        "--player-weeks-path",
        help="Path to arc_player_weeks (.csv/.parquet).",
    ),
    player_seasons_path: Path = typer.Option(
        DEFAULT_PLAYER_SEASONS_PATH,
        "--player-seasons-path",
        help="Path to arc_player_seasons (.csv/.parquet).",
    ),
    output_dir: Path = typer.Option(
        DEFAULT_SUMMARY_DIR,
        "--output-dir",
        help="Directory for baseline summary outputs.",
    ),
    small_sample_threshold: int = typer.Option(
        10,
        "--small-sample-threshold",
        min=1,
        help="Threshold used to flag small cohorts.",
    ),
) -> None:
    """Build ARC cohort baseline summary tables from PR2 outputs."""

    try:
        player_weeks = _read_table(player_weeks_path)
        player_seasons = _read_table(player_seasons_path)
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    cohort_baselines = compute_cohort_baselines(
        player_seasons,
        player_weeks,
        small_sample_threshold=small_sample_threshold,
    )
    career_year_baselines = compute_career_year_baselines(
        player_seasons,
        player_weeks,
        small_sample_threshold=small_sample_threshold,
    )

    cohort_csv = output_dir / "arc_cohort_baselines.csv"
    career_year_csv = output_dir / "arc_career_year_baselines.csv"
    export_csv(cohort_baselines, cohort_csv)
    export_csv(career_year_baselines, career_year_csv)

    parquet_written: list[str] = []
    for df, output in (
        (cohort_baselines, output_dir / "arc_cohort_baselines.parquet"),
        (career_year_baselines, output_dir / "arc_career_year_baselines.parquet"),
    ):
        try:
            export_parquet(df, output)
            parquet_written.append(str(output))
        except RuntimeError:
            continue

    typer.echo("Built ARC baseline summary tables")
    typer.echo(
        "Rows: "
        f"cohort_baselines={len(cohort_baselines):,}, "
        f"career_year_baselines={len(career_year_baselines):,}"
    )
    typer.echo(f"CSV outputs: {cohort_csv}, {career_year_csv}")
    if parquet_written:
        typer.echo("Parquet outputs: " + ", ".join(parquet_written))
    else:
        typer.echo("Parquet outputs skipped (install pyarrow to enable)")


@app.command("build-promoted-handoff")
def build_promoted_handoff_command(
    cohort_baselines_path: Path = typer.Option(
        DEFAULT_COHORT_BASELINES_PATH,
        "--cohort-baselines-path",
        help="Path to arc_cohort_baselines (.csv/.parquet).",
    ),
    career_year_baselines_path: Path = typer.Option(
        DEFAULT_CAREER_BASELINES_PATH,
        "--career-year-baselines-path",
        help="Path to arc_career_year_baselines (.csv/.parquet).",
    ),
    output_path: Path = typer.Option(
        DEFAULT_PROMOTED_HANDOFF_PATH,
        "--output-path",
        help="Canonical promoted handoff artifact path.",
    ),
) -> None:
    """Build the single promoted handoff artifact for downstream consumers."""

    try:
        cohort_baselines = _read_table(cohort_baselines_path)
        career_year_baselines = _read_table(career_year_baselines_path)
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    handoff = build_promoted_handoff(
        cohort_baselines,
        career_year_baselines,
        arc_version=__version__,
    )
    export_csv(handoff, output_path)

    typer.echo("Built ARC promoted handoff artifact")
    typer.echo(f"Rows: {len(handoff):,}")
    typer.echo(f"Output: {output_path}")



if __name__ == "__main__":
    app()
