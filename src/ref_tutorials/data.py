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


def latest_successful_execution(execution_group: Any) -> Any | None:
    """Return the most recent successful execution in an execution group.

    Parameters
    ----------
    execution_group
        An execution group as returned by ``climate_ref_client``.
        It must expose ``.executions``, a list of executions with
        ``.successful``, ``.retracted`` and ``.created_at`` attributes.

    Returns
    -------
    climate_ref_client.models.Execution or None
        The newest execution that succeeded and has not been retracted,
        or ``None`` if the group has no such execution.
    """
    successful = [e for e in execution_group.executions if e.successful and not e.retracted]
    return max(successful, key=lambda e: e.created_at, default=None)


def create_cmip7_sample_data(directory: Path = Path("data/cmip7-sample")) -> Path:
    """Write a tiny synthetic CMIP7-style ``tas`` and ``areacella`` pair.

    The files follow the CMIP7 DRS layout so REF's CMIP7 adapter can discover
    them. They are teaching data, not output from a real climate model.
    """
    import numpy as np
    import xarray as xr

    directory = Path(directory)
    common = {
        "mip_era": "CMIP7",
        "activity_id": "CMIP",
        "institution_id": "Tutorial",
        "source_id": "Tutorial-Model",
        "experiment_id": "historical",
        "variant_label": "r1i1p1f1",
        "grid_label": "g100",
        "region": "glb",
        "realm": "atmos",
        "nominal_resolution": "100 km",
        "license_id": "CC0-1.0",
    }
    drs_root = directory / "MIP-DRS7" / "CMIP7"
    model_root = drs_root / "CMIP" / "Tutorial" / "Tutorial-Model" / "historical" / "r1i1p1f1" / "glb"
    lat = np.array([-60.0, 0.0, 60.0])
    lon = np.array([0.0, 90.0, 180.0, 270.0])
    months = np.arange(120)
    time = pd.date_range("1850-01-01", periods=len(months), freq="MS")
    tas = (
        280.0
        + 0.02 * months[:, None, None] / 12
        + 3.0 * np.sin(2 * np.pi * months[:, None, None] / 12)
        - 0.05 * np.abs(lat[None, :, None])
        + np.zeros((1, 1, len(lon)))
    )

    tas_dir = model_root / "mon" / "tas" / "tavg-h2m-hxy-u" / "g100" / "v1"
    tas_dir.mkdir(parents=True, exist_ok=True)
    xr.Dataset(
        {"tas": (("time", "lat", "lon"), tas.astype("float32"), {"units": "K"})},
        coords={"time": time, "lat": lat, "lon": lon},
        attrs={
            **common,
            "variable_id": "tas",
            "frequency": "mon",
            "branding_suffix": "tavg-h2m-hxy-u",
            "branded_variable": "tas_tavg-h2m-hxy-u",
            "tracking_id": "synthetic-tas",
        },
    ).to_netcdf(
        tas_dir / "tas_tavg-h2m-hxy-u_mon_glb_g100_Tutorial-Model_historical_r1i1p1f1_185001-185912.nc"
    )

    area = 1e12 * np.cos(np.deg2rad(lat))[:, None] * np.ones((1, len(lon)))
    area_dir = model_root / "fx" / "areacella" / "u" / "g100" / "v1"
    area_dir.mkdir(parents=True, exist_ok=True)
    xr.Dataset(
        {"areacella": (("lat", "lon"), area, {"units": "m2"})},
        coords={"lat": lat, "lon": lon},
        attrs={
            **common,
            "variable_id": "areacella",
            "frequency": "fx",
            "branding_suffix": "u",
            "branded_variable": "areacella_u",
            "tracking_id": "synthetic-areacella",
        },
    ).to_netcdf(area_dir / "areacella_u_fx_glb_g100_Tutorial-Model_historical_r1i1p1f1.nc")

    # The current REF adapter searches ten levels below the supplied root.
    # Starting at the activity directory includes the version-level files.
    return drs_root / "CMIP"


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
