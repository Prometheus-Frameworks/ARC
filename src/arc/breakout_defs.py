"""Event and finish classification helpers for ARC tables."""

from __future__ import annotations

import pandas as pd

from arc.config import (
    ELITE_SEASON_FINISH_CUTOFFS,
    STARTER_SEASON_FINISH_CUTOFFS,
    WEEKLY_DUD_FINISH_THRESHOLDS,
    WEEKLY_SPIKE_FINISH_THRESHOLDS,
)


def is_spike_week(position: str, weekly_pos_finish: int | None) -> bool:
    """Return whether a weekly finish qualifies as a position spike week."""

    if pd.isna(weekly_pos_finish):
        return False
    threshold = WEEKLY_SPIKE_FINISH_THRESHOLDS.get(str(position).upper())
    return threshold is not None and int(weekly_pos_finish) <= threshold


def is_dud_week(position: str, weekly_pos_finish: int | None) -> bool:
    """Return whether a weekly finish qualifies as a position dud week."""

    if pd.isna(weekly_pos_finish):
        return False
    threshold = WEEKLY_DUD_FINISH_THRESHOLDS.get(str(position).upper())
    return threshold is not None and int(weekly_pos_finish) > threshold


def classify_season_finish(position: str, seasonal_finish: int | None) -> str | None:
    """Classify season finish into top_tier/starter_tier/other."""

    if pd.isna(seasonal_finish):
        return None

    pos = str(position).upper()
    finish = int(seasonal_finish)
    elite_cutoff = ELITE_SEASON_FINISH_CUTOFFS.get(pos)
    starter_cutoff = STARTER_SEASON_FINISH_CUTOFFS.get(pos)

    if elite_cutoff is not None and finish <= elite_cutoff:
        return "top_tier"
    if starter_cutoff is not None and finish <= starter_cutoff:
        return "starter_tier"
    return "other"
