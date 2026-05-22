"""Unit tests for the ``ref_tutorials`` helper package."""

from __future__ import annotations

from dataclasses import dataclass, field

import matplotlib
import pandas as pd
import pytest

from ref_tutorials import (
    metric_values_to_dataframe,
    model_comparison_figure,
    save_figure,
    set_publication_style,
)
from ref_tutorials.plotting import PUBLICATION_RCPARAMS

# The Agg backend is selected in conftest.py before this module is imported.


@dataclass
class _Dimensions:
    additional_properties: dict = field(default_factory=dict)


@dataclass
class _MetricValue:
    value: float
    dimensions: _Dimensions

    @classmethod
    def make(cls, value: float, **dims: object) -> _MetricValue:
        return cls(value=value, dimensions=_Dimensions(additional_properties=dict(dims)))


def test_metric_values_to_dataframe_flattens_dimensions():
    values = [
        _MetricValue.make(1.0, source_id="ModelA", statistic="rmse"),
        _MetricValue.make(2.0, source_id="ModelB", statistic="rmse"),
    ]

    df = metric_values_to_dataframe(values)

    assert set(df.columns) == {"source_id", "statistic", "value"}
    assert len(df) == 2
    assert df.loc[df["source_id"] == "ModelB", "value"].iloc[0] == 2.0


def test_metric_values_to_dataframe_normalises_none_strings():
    df = metric_values_to_dataframe([_MetricValue.make(1.0, region="None")])

    assert pd.isna(df["region"].iloc[0])


def test_metric_values_to_dataframe_drops_duplicate_rows():
    value = _MetricValue.make(1.0, source_id="ModelA", statistic="rmse")

    df = metric_values_to_dataframe([value, value])

    assert len(df) == 1


def test_metric_values_to_dataframe_empty_input():
    df = metric_values_to_dataframe([])

    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_set_publication_style_applies_rcparams():
    matplotlib.rcParams["font.size"] = 99  # Pollute first.

    set_publication_style()

    assert matplotlib.rcParams["font.size"] == PUBLICATION_RCPARAMS["font.size"]


def test_model_comparison_figure_returns_fig_and_axes():
    df = pd.DataFrame(
        {
            "source_id": ["ModelA", "ModelB", "ModelC"],
            "value": [3.0, 1.0, 2.0],
        }
    )

    fig, ax = model_comparison_figure(df, title="Test")

    # One bar per model.
    assert len(ax.patches) == 3
    assert ax.get_title() == "Test"


def test_model_comparison_figure_aggregates_ensemble_members():
    # Two members of ModelA should collapse to a single bar.
    df = pd.DataFrame(
        {
            "source_id": ["ModelA", "ModelA", "ModelB"],
            "value": [1.0, 3.0, 5.0],
        }
    )

    fig, ax = model_comparison_figure(df)

    assert len(ax.patches) == 2


def test_save_figure_writes_png_and_pdf(tmp_path):
    df = pd.DataFrame({"source_id": ["ModelA"], "value": [1.0]})
    fig, _ = model_comparison_figure(df)

    written = save_figure(fig, tmp_path / "figure")

    suffixes = sorted(p.suffix for p in written)
    assert suffixes == [".pdf", ".png"]
    assert all(p.exists() and p.stat().st_size > 0 for p in written)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
