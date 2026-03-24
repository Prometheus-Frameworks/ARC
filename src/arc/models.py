"""Canonical schema contracts for ARC tables.

These Pydantic models define the stable interfaces that downstream modules
and future PRs should target.
"""

from pydantic import BaseModel, Field


class ArcPlayerSeason(BaseModel):
    """Canonical player-season record for ARC."""

    player_id: str
    player_name: str
    season: int
    position: str
    team: str | None = None
    age: float | None = None
    age_bucket: str | None = None
    career_year: int | None = None
    games_played: int | None = None
    ppg: float | None = None
    season_points: float | None = None
    positional_finish: int | None = None
    top_tier_finish: bool | None = Field(default=None)
    starter_tier_finish: bool | None = Field(default=None)


class ArcPlayerWeek(BaseModel):
    """Canonical player-week record for ARC."""

    player_id: str
    player_name: str
    season: int
    week: int
    position: str
    fantasy_points: float | None = None
    weekly_pos_finish: int | None = None
    spike_flag: bool | None = None
    dud_flag: bool | None = None


class ArcCohortBaseline(BaseModel):
    """Cohort-level summary statistics by position/career-year/age-bucket."""

    position: str
    career_year: int
    age_bucket: str
    sample_size: int
    avg_ppg: float | None = None
    median_ppg: float | None = None
    ppg_std: float | None = None
    avg_season_points: float | None = None
    median_season_points: float | None = None
    avg_games_played: float | None = None
    spike_rate: float | None = None
    dud_rate: float | None = None
    elite_finish_rate: float | None = None
    starter_finish_rate: float | None = None
    is_small_sample: bool
    small_sample_threshold: int


class ArcCareerYearBaseline(BaseModel):
    """Fallback cohort statistics by position/career-year only."""

    position: str
    career_year: int
    sample_size: int
    avg_ppg: float | None = None
    median_ppg: float | None = None
    ppg_std: float | None = None
    avg_season_points: float | None = None
    median_season_points: float | None = None
    avg_games_played: float | None = None
    spike_rate: float | None = None
    dud_rate: float | None = None
    elite_finish_rate: float | None = None
    starter_finish_rate: float | None = None
    is_small_sample: bool
    small_sample_threshold: int


class ArcTrajectoryScore(BaseModel):
    """Expected-vs-actual trajectory record for player-season evaluation."""

    player_id: str
    player_name: str
    season: int
    position: str
    career_year: int | None = None
    age_bucket: str | None = None
    actual_ppg: float | None = None
    expected_ppg: float | None = None
    delta_vs_expected: float | None = None
    percentile_within_cohort: float | None = None
    trajectory_label: str | None = None


class ArcPromotedHandoff(BaseModel):
    """Single promoted handoff row for downstream ARC consumers."""

    build_timestamp_utc: str
    arc_version: str
    baseline_level: str
    position: str
    career_year: int
    age_bucket: str | None = None
    sample_size: int
    avg_ppg: float | None = None
    median_ppg: float | None = None
    ppg_std: float | None = None
    avg_season_points: float | None = None
    median_season_points: float | None = None
    avg_games_played: float | None = None
    spike_rate: float | None = None
    dud_rate: float | None = None
    elite_finish_rate: float | None = None
    starter_finish_rate: float | None = None
    is_small_sample: bool
    small_sample_threshold: int
