"""Scaffold event/finish classification helpers for ARC."""


def is_spike_week(position: str, weekly_pos_finish: int | None) -> bool:
    """Return spike-week classification using provisional positional thresholds."""

    _ = (position, weekly_pos_finish)
    return False


def is_dud_week(position: str, weekly_pos_finish: int | None) -> bool:
    """Return dud-week classification using provisional positional thresholds."""

    _ = (position, weekly_pos_finish)
    return False


def classify_season_finish(position: str, seasonal_finish: int | None) -> str | None:
    """Classify season finish tier (elite/starter/other).

    PR1 returns `None` pending finalized threshold logic.
    """

    _ = (position, seasonal_finish)
    return None
