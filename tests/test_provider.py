"""Tests for the custom tutorial diagnostic provider.

These tests need ``climate_ref_core`` (installed via the ``climate-ref``
dependency). They are skipped when it is unavailable, so the lightweight
helper-package tests can still run on their own.

Actually *running* the diagnostic against data is covered by executing
notebook 04 in CI; here we only check the provider is wired up correctly.
"""

from __future__ import annotations

import pytest

pytest.importorskip("climate_ref_core")

from ref_tutorials.provider import (  # noqa: E402
    AnnualMeanGlobalMeanTas,
    build_provider,
    provider,
)


def test_provider_registers_the_diagnostic():
    diagnostic = provider.get("annual-mean-global-mean-tas")

    assert isinstance(diagnostic, AnnualMeanGlobalMeanTas)
    assert diagnostic.name == "Annual Mean Global Mean Temperature"


def test_build_provider_is_independent():
    # Each call yields a fresh provider with the diagnostic registered.
    fresh = build_provider()

    assert fresh is not provider
    assert fresh.get("annual-mean-global-mean-tas") is not None


def test_diagnostic_requires_cmip6_tas():
    from climate_ref_core.datasets import SourceDatasetType

    diagnostic = AnnualMeanGlobalMeanTas()
    requirement = diagnostic.data_requirements[0][0]

    assert requirement.source_type == SourceDatasetType.CMIP6
    assert requirement.filters[0].facets == {"variable_id": ("tas",)}
