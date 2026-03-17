# ARC: Age and Role Curves

ARC is a historical fantasy football cohort engine designed for research-grade analysis of player outcomes over time. It is built to model how players perform relative to peers grouped by **position**, **career year**, and **age bucket**.

## Why ARC exists

Most fantasy analyses over-index on raw age. ARC treats **career year as the primary axis** because it better reflects football development windows (learning curve, role growth, workload accumulation, and survivorship effects). Age remains important as a **secondary normalization layer** so we can separate a Year-3 player at age 22 from a Year-3 player at age 25.

The goal is cohort intelligence, not hot takes:
- Historical player-season cohort tables
- Historical player-week outcome tables
- Cohort baseline summaries
- Trajectory/deviation scores versus cohort expectations

ARC is intended to power downstream tools such as player pages, dynasty outlook frameworks, and trajectory analysis workflows.

## What PR1 includes

PR1 bootstraps the repository as a clean Python package and research workspace:
- `src/arc` package scaffold with typed models and placeholder analysis modules
- Config stubs for positions, buckets, and thresholds
- Lightweight CLI entrypoint for package validation
- Documentation for methodology, metric definitions, and roadmap
- Data/output directory structure for future ETL and exports
- Minimal import test coverage to confirm scaffold integrity

This PR intentionally does **not** implement heavy ingestion, full historical processing, or production scoring logic.

## Planned canonical tables

ARC will standardize downstream work around these canonical tables:

1. `arc_player_seasons`
   - One row per player-season with age/career metadata and season-level outcomes.
2. `arc_player_weeks`
   - One row per player-week with weekly finishes and event flags (spike/dud).
3. `arc_cohort_baselines`
   - Cohort summaries by position + career year + age bucket.
4. `arc_trajectory_scores`
   - Expected-vs-actual deltas and relative trajectory labels.

## High-level roadmap

- **PR2:** Build player-season and player-week historical cohort tables.
- **PR3:** Compute cohort baselines by position/career-year/age-bucket slices.
- **PR4:** Add trajectory scoring, percentile framing, and deviation labels.

## Future directions

Potential expansions beyond core PR1–PR4:
- Draft capital context layers
- Usage archetypes (target share, touch share, role clusters)
- Next-year hit rate modeling
- Comparable player trajectory engine

## Quick start

```bash
python -m arc.cli info
python -m arc.cli validate-config
```

Or install and use console script:

```bash
pip install -e .
arc info
```
