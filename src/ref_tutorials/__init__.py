"""Shared helpers for the Climate REF training notebooks.

This package keeps the notebooks short and narrative by hiding the
repetitive detail of talking to the REF API, reshaping responses, and
producing a consistent publication-quality plotting style.

The public interface is intentionally small and stable:

- :func:`get_client` -- build a REF API client.
- :func:`metric_values_to_dataframe` -- turn API metric values into a tidy
  :class:`pandas.DataFrame`.
- :func:`set_publication_style` -- apply a consistent matplotlib style.
- :func:`model_comparison_figure` -- build a multi-model comparison figure.
- :func:`save_figure` -- save a figure in publication-ready formats.
- :func:`fetch_sample_data` -- download small CMIP6 sample data via the REF CLI.
"""

from ref_tutorials.client import DEFAULT_API_URL, get_client
from ref_tutorials.data import fetch_sample_data, metric_values_to_dataframe
from ref_tutorials.plotting import (
    model_comparison_figure,
    save_figure,
    set_publication_style,
)

__all__ = [
    "DEFAULT_API_URL",
    "fetch_sample_data",
    "get_client",
    "metric_values_to_dataframe",
    "model_comparison_figure",
    "save_figure",
    "set_publication_style",
]
