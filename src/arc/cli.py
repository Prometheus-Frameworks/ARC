"""CLI entrypoint for ARC scaffold validation commands."""

import json

import typer

from arc import __version__
from arc.config import (
    AGE_BUCKETS,
    ELITE_SEASON_FINISH_CUTOFFS,
    STARTER_SEASON_FINISH_CUTOFFS,
    SUPPORTED_POSITIONS,
    WEEKLY_DUD_FINISH_THRESHOLDS,
    WEEKLY_SPIKE_FINISH_THRESHOLDS,
)

app = typer.Typer(help="ARC command line interface.")


@app.command("info")
def info() -> None:
    """Print project and stage information."""

    typer.echo("ARC (Age and Role Curves)")
    typer.echo("Stage: PR1 scaffold")
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


if __name__ == "__main__":
    app()
