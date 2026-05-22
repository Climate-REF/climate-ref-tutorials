"""A self-contained custom diagnostic provider for the tutorials.

The REF runs diagnostics from *providers* -- packages that know how to compute a family of diagnostics.
Rather than depending on the REF's bundled example provider,
the tutorials define their own minimal one here, so notebook 04 can show a complete,
real custom provider that lives entirely in this repository.

The diagnostic computes the annual-mean, area-weighted global-mean near-surface air
temperature (``tas``) of a CMIP6 dataset, and then registers a representative slice of
everything a real diagnostic produces:

- **scalar** metric values (the period mean, minimum and maximum);
- a **series** metric value (the annual-mean timeseries itself);
- **figures** (a timeseries plot and an anomaly plot).
"""

from __future__ import annotations

import importlib.metadata
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # Diagnostics run headless; no display is available.

import matplotlib.pyplot as plt  # noqa: E402
import xarray as xr  # noqa: E402
from climate_ref_core.constraints import (  # noqa: E402
    AddSupplementaryDataset,
    RequireContiguousTimerange,
)
from climate_ref_core.datasets import FacetFilter, SourceDatasetType  # noqa: E402
from climate_ref_core.diagnostics import (  # noqa: E402
    DataRequirement,
    Diagnostic,
    ExecutionDefinition,
    ExecutionResult,
)
from climate_ref_core.metric_values.typing import SeriesMetricValue  # noqa: E402
from climate_ref_core.providers import DiagnosticProvider  # noqa: E402
from climate_ref_core.pycmec.metric import CMECMetric  # noqa: E402
from climate_ref_core.pycmec.output import CMECOutput, OutputCV  # noqa: E402

#: Name of the NetCDF file the diagnostic writes into its output directory.
_OUTPUT_FILENAME = "annual_mean_global_mean_tas.nc"

#: Figure filenames written into the output directory.
_TIMESERIES_PLOT = "timeseries.png"
_ANOMALY_PLOT = "anomaly.png"


def _try_version() -> str:
    """Return the installed package version, or a placeholder when run from source."""
    try:
        return importlib.metadata.version("climate-ref-tutorials")
    except importlib.metadata.PackageNotFoundError:  # pragma: no cover - source runs
        return "0.0.0+local"


def calculate_annual_mean_global_mean(input_files: list[Path]) -> xr.Dataset:
    """Compute the annual-mean, area-weighted global-mean timeseries.

    Parameters
    ----------
    input_files
        Input NetCDF files for a single dataset. Must include the ``tas``
        variable and the ``areacella`` cell-area field.

    Returns
    -------
    xarray.Dataset
        The annual-mean global-mean timeseries.
    """
    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
    ds = xr.open_mfdataset(
        input_files, combine="by_coords", chunks=None, decode_times=time_coder
    )

    annual_mean = ds.resample(time="YS").mean()
    # resample turns datetime bounds into object arrays; drop them before the
    # weighted mean to avoid a dtype error.
    if "time_bnds" in annual_mean:
        annual_mean = annual_mean.drop_vars("time_bnds")

    return annual_mean.weighted(ds.areacella.fillna(0)).mean(
        dim=["lat", "lon"], keep_attrs=True
    )


def _years(ds: xr.Dataset) -> list[int]:
    """Return the calendar years of a dataset's time axis as plain integers."""
    return [int(year) for year in ds["time"].dt.year.values]


def make_figures(ds: xr.Dataset, output_directory: Path) -> dict[str, Path]:
    """Draw the diagnostic's figures and save them as PNGs.

    Two deliberately simple figures: the annual-mean global-mean ``tas``
    timeseries, and its anomaly relative to the period mean.

    Parameters
    ----------
    ds
        The annual-mean global-mean dataset (must contain ``tas`` over ``time``).
    output_directory
        Directory to write the PNG files into.

    Returns
    -------
    dict[str, pathlib.Path]
        Mapping of a short caption to each written figure path.
    """
    years = _years(ds)
    tas = ds["tas"].values

    timeseries_path = output_directory / _TIMESERIES_PLOT
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(years, tas, marker="o", color="#1f77b4")
    ax.set_xlabel("Year")
    ax.set_ylabel("Global-mean tas (K)")
    ax.set_title("Annual-mean global-mean near-surface air temperature")
    fig.tight_layout()
    fig.savefig(timeseries_path, dpi=150)
    plt.close(fig)

    anomaly_path = output_directory / _ANOMALY_PLOT
    anomaly = tas - tas.mean()
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#d62728" if a >= 0 else "#1f77b4" for a in anomaly]
    ax.bar(years, anomaly, color=colors)
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_xlabel("Year")
    ax.set_ylabel("tas anomaly (K)")
    ax.set_title("Annual-mean tas anomaly relative to the period mean")
    fig.tight_layout()
    fig.savefig(anomaly_path, dpi=150)
    plt.close(fig)

    return {
        "Annual-mean global-mean tas timeseries": timeseries_path,
        "Annual-mean tas anomaly": anomaly_path,
    }


def _scalar_metric_bundle(
    ds: xr.Dataset, input_selectors: dict[str, str]
) -> CMECMetric:
    """Build a CMEC metric bundle holding the scalar summary statistics."""
    tas = ds["tas"]
    bundle = {
        "DIMENSIONS": {
            "json_structure": ["region", "metric", "statistic"],
            "region": {"global": {}},
            "metric": {"tas": {}},
            "statistic": {"mean": {}, "min": {}, "max": {}},
        },
        "RESULTS": {
            "global": {
                "tas": {
                    "mean": float(tas.mean()),
                    "min": float(tas.min()),
                    "max": float(tas.max()),
                }
            }
        },
    }
    return CMECMetric(**bundle).prepend_dimensions(input_selectors)


def _series_values(
    ds: xr.Dataset, input_selectors: dict[str, str]
) -> list[SeriesMetricValue]:
    """Build the series metric value: the annual-mean tas timeseries."""
    return [
        SeriesMetricValue(
            dimensions={"region": "global", "metric": "tas", **input_selectors},
            values=[float(v) for v in ds["tas"].values],
            index=_years(ds),
            index_name="year",
            attributes={"units": "K", "long_name": "Annual-mean global-mean tas"},
        )
    ]


class AnnualMeanGlobalMeanTas(Diagnostic):
    """Annual-mean, global-mean near-surface air temperature.

    A minimal custom diagnostic for the tutorials. It requires CMIP6 ``tas``
    data, and pulls in the matching ``areacella`` cell-area field as a
    supplementary dataset so the global mean can be area-weighted.

    Its execution registers scalar metric values, a series metric value, and
    two figures -- a representative cross-section of what a real diagnostic
    produces.
    """

    name = "Annual Mean Global Mean Temperature"
    slug = "annual-mean-global-mean-tas"

    data_requirements = (
        (
            DataRequirement(
                source_type=SourceDatasetType.CMIP6,
                filters=(FacetFilter(facets={"variable_id": ("tas",)}),),
                group_by=("source_id", "experiment_id", "variant_label"),
                constraints=(
                    RequireContiguousTimerange(group_by=("instance_id",)),
                    AddSupplementaryDataset.from_defaults(
                        "areacella", SourceDatasetType.CMIP6
                    ),
                ),
            ),
        ),
    )
    facets = (
        "source_id",
        "experiment_id",
        "variant_label",
        "region",
        "metric",
        "statistic",
    )

    def execute(self, definition: ExecutionDefinition) -> None:
        """Compute the diagnostic: write the output NetCDF and the figures."""
        input_datasets = definition.datasets[SourceDatasetType.CMIP6]
        result = calculate_annual_mean_global_mean(input_datasets.path.to_list())
        if "time_bnds" in result:
            result = result.drop_vars("time_bnds")
        result.to_netcdf(definition.output_directory / _OUTPUT_FILENAME)

        make_figures(result, definition.output_directory)

    def build_execution_result(self, definition: ExecutionDefinition) -> ExecutionResult:
        """Package the output into an :class:`ExecutionResult`.

        ``execute`` has already written the NetCDF file and the figures. Here we
        register the scalar metric values, the series metric value, and the
        figures so the REF records them.
        """
        time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
        ds = xr.open_dataset(
            definition.output_directory / _OUTPUT_FILENAME, decode_times=time_coder
        )

        selectors = definition.datasets[SourceDatasetType.CMIP6].selector_dict()
        input_selectors: dict[str, Any] = {
            "source_id": selectors["source_id"],
            "experiment_id": selectors["experiment_id"],
            "variant_label": selectors["variant_label"],
        }

        # Register the figures written by execute().
        output_bundle = CMECOutput.create_template()
        captions = {
            _TIMESERIES_PLOT: "Annual-mean global-mean tas timeseries",
            _ANOMALY_PLOT: "Annual-mean tas anomaly relative to the period mean",
        }
        for filename, caption in captions.items():
            relative_path = str(
                definition.as_relative_path(definition.output_directory / filename)
            )
            output_bundle[OutputCV.PLOTS.value][relative_path] = {
                OutputCV.FILENAME.value: relative_path,
                OutputCV.LONG_NAME.value: caption,
                OutputCV.DESCRIPTION.value: caption,
                OutputCV.DIMENSIONS.value: input_selectors,
            }

        return ExecutionResult.build_from_output_bundle(
            definition,
            cmec_output_bundle=output_bundle,
            cmec_metric_bundle=_scalar_metric_bundle(ds, input_selectors),
            series=_series_values(ds, input_selectors),
        )


def build_provider() -> DiagnosticProvider:
    """Create the tutorial diagnostic provider and register its diagnostics."""
    provider = DiagnosticProvider("Tutorial", _try_version())
    provider.register(AnnualMeanGlobalMeanTas())
    return provider


#: The tutorial provider, ready to use. Import this in notebook 04.
provider = build_provider()
