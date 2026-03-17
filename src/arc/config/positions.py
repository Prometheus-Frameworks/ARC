"""Supported position constants for ARC.

PR1 scope limits position modeling to traditional fantasy positions.
"""

from typing import Final

SUPPORTED_POSITIONS: Final[tuple[str, ...]] = ("QB", "RB", "WR", "TE")
CORE_POSITIONS: Final[set[str]] = set(SUPPORTED_POSITIONS)
