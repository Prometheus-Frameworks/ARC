"""Scaffold export utilities for ARC outputs."""

from pathlib import Path

import pandas as pd


def export_csv(df: pd.DataFrame, path: str | Path) -> None:
    """Export a DataFrame to CSV.

    This helper is intentionally lightweight for PR1.
    """

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def export_parquet(df: pd.DataFrame, path: str | Path) -> None:
    """Export a DataFrame to Parquet.

    This helper is intentionally lightweight for PR1.
    """

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
