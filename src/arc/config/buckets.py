"""Bucket definitions used for cohort segmentation.

These defaults are intentionally simple and easy to edit in future PRs.
"""

from typing import Final

AGE_BUCKETS: Final[tuple[str, ...]] = (
    "<22",
    "22-23",
    "24-25",
    "26-27",
    "28-29",
    "30+",
)

CAREER_YEAR_NOTES: Final[dict[str, str]] = {
    "1": "Rookie season",
    "2": "Second-year development window",
    "3": "Typical early-prime transition",
    "4+": "Role stabilization and veteran arcs",
}
