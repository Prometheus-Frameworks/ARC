"""Smoke tests to ensure ARC PR1 scaffold imports cleanly."""


def test_config_imports() -> None:
    from arc.config import buckets, positions, thresholds

    assert buckets is not None
    assert positions is not None
    assert thresholds is not None


def test_models_import() -> None:
    from arc import models

    assert models is not None


def test_cli_import() -> None:
    from arc import cli

    assert cli is not None


def test_placeholder_module_imports() -> None:
    from arc import breakout_defs, cohort_builder, exports, metrics, trajectory

    assert breakout_defs is not None
    assert cohort_builder is not None
    assert metrics is not None
    assert trajectory is not None
    assert exports is not None
