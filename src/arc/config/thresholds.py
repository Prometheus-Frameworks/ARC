"""Provisional threshold defaults for ARC.

These are PR1 scaffold values and should be tuned using historical data.
"""

from typing import Final

WEEKLY_SPIKE_FINISH_THRESHOLDS: Final[dict[str, int]] = {
    "QB": 8,
    "RB": 12,
    "WR": 12,
    "TE": 6,
}

WEEKLY_DUD_FINISH_THRESHOLDS: Final[dict[str, int]] = {
    "QB": 20,
    "RB": 36,
    "WR": 36,
    "TE": 18,
}

ELITE_SEASON_FINISH_CUTOFFS: Final[dict[str, int]] = {
    "QB": 8,
    "RB": 12,
    "WR": 12,
    "TE": 6,
}

STARTER_SEASON_FINISH_CUTOFFS: Final[dict[str, int]] = {
    "QB": 12,
    "RB": 24,
    "WR": 24,
    "TE": 12,
}
