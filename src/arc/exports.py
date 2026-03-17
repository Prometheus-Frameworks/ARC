"""Export utilities for ARC output tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def _ensure_parent(path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def export_csv(df: pd.DataFrame, path: str | Path) -> None:
    """Export a DataFrame to CSV, creating parent directories when needed."""

    output_path = _ensure_parent(path)
    df.to_csv(output_path, index=False)


def export_parquet(df: pd.DataFrame, path: str | Path) -> None:
    """Export a DataFrame to Parquet, creating parent directories when needed."""

    output_path = _ensure_parent(path)
    try:
        df.to_parquet(output_path, index=False)
    except ImportError as exc:
        raise RuntimeError(
            "Parquet export requires an optional engine such as pyarrow."
        ) from exc
