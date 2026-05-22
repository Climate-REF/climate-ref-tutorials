"""Reshaping REF API responses and fetching sample data.

:func:`metric_values_to_dataframe` is the deepest, purest function in this
package: given the metric values returned by the REF API it produces a tidy :class:`pandas.DataFrame`.
"""

import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pandas as pd


def metric_values_to_dataframe(values: Iterable[Any]) -> pd.DataFrame:
    """Convert REF API metric values into a :class:`pandas.DataFrame`.

    Each metric value has a set of *dimensions* (model, experiment, statistic, ...) and a scalar ``value``.
    This function flattens them into one row per metric value,
    with one column per dimension plus a ``value`` column.

    Parameters
    ----------
    values
        An iterable of metric value objects as returned by ``climate_ref_client``.
        Each object must expose ``.dimensions.additional_properties`` (a mapping) and ``.value``.

    Returns
    -------
    pandas.DataFrame
        One row per metric value. Columns are the dimension keys plus ``value``.
        The literal string ``"None"`` is normalised to :data:`pandas.NA` and exact duplicate rows are dropped.
    """
    frame = pd.DataFrame({**value.dimensions.additional_properties, "value": value.value} for value in values)
    return frame.replace("None", pd.NA).drop_duplicates().reset_index(drop=True)


def fetch_sample_data(force_cleanup: bool = False) -> Path:
    """Download the small CMIP6 sample dataset used by the local-run notebooks.

    This wraps the REF CLI's sample-data fetch so the notebooks do not have to source CMIP6 data themselves.
    The data is small and intended only for demonstration.

    Parameters
    ----------
    force_cleanup
        If ``True``, remove any previously fetched sample data first.

    Returns
    -------
    pathlib.Path
        Directory containing the fetched sample data.

    Raises
    ------
    ModuleNotFoundError
        If the ``climate-ref`` package is not installed.
    """
    test_data_dir = str(Path(__file__).parents[2] / "tests" / "test-data")
    os.environ.setdefault("REF_TEST_DATA_DIR", test_data_dir)
    Path(test_data_dir).mkdir(parents=True, exist_ok=True)

    try:
        from climate_ref.testing import TEST_DATA_DIR
        from climate_ref.testing import fetch_sample_data as _fetch
    except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
        msg = (
            "The 'climate-ref' package is not installed. Install it with "
            "'uv sync' to run the local-execution notebooks."
        )
        raise ModuleNotFoundError(msg) from exc

    assert TEST_DATA_DIR == Path(test_data_dir)
    _fetch(force_cleanup=force_cleanup)
    return Path(test_data_dir) / "sample-data"
