"""A self-contained custom diagnostic provider for the tutorials.

The REF runs diagnostics from *providers* -- packages that know how to compute
a family of diagnostics. Rather than depending on the REF's bundled example
provider, the tutorials define their own minimal one here, so notebook 04 can
show a complete, real custom provider that lives entirely in this repository.

The diagnostic itself is deliberately small: it computes the annual-mean,
area-weighted global-mean near-surface air temperature (``tas``) timeseries of
a CMIP6 dataset. It is a faithful but trimmed illustration of how a real
diagnostic is structured.

Importing this module requires ``climate-ref`` (which provides
``climate_ref_core``) to be installed. It is intentionally *not* re-exported
from :mod:`ref_tutorials` so that the API-only notebooks (01-03) do not need it.
"""

from __future__ import annotations

import importlib.metadata
from pathlib import Path
from typing import Any

import xarray as xr
from climate_ref_core.constraints import (
    AddSupplementaryDataset,
    RequireContiguousTimerange,
)
from climate_ref_core.datasets import FacetFilter, SourceDatasetType
from climate_ref_core.diagnostics import (
    DataRequirement,
    Diagnostic,
    ExecutionDefinition,
    ExecutionResult,
)
from climate_ref_core.providers import DiagnosticProvider
from climate_ref_core.pycmec.metric import CMECMetric
from climate_ref_core.pycmec.output import CMECOutput

#: Name of the NetCDF file the diagnostic writes into its output directory.
_OUTPUT_FILENAME = "annual_mean_global_mean_tas.nc"


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


def _metric_bundle(input_selectors: dict[str, str]) -> CMECMetric:
    """Build a minimal CMEC metric bundle describing the result."""
    bundle = {
        "DIMENSIONS": {
            "json_structure": ["region", "metric", "statistic"],
            "region": {"global": {}},
            "metric": {"tas": {}},
            "statistic": {"mean": {}},
        },
        "RESULTS": {"global": {"tas": {"mean": 0.0}}},
    }
    return CMECMetric(**bundle).prepend_dimensions(input_selectors)


class AnnualMeanGlobalMeanTas(Diagnostic):
    """Annual-mean, global-mean near-surface air temperature.

    A minimal custom diagnostic for the tutorials. It requires CMIP6 ``tas``
    data, and pulls in the matching ``areacella`` cell-area field as a
    supplementary dataset so the global mean can be area-weighted.
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
        """Compute the diagnostic and write its output NetCDF file."""
        input_datasets = definition.datasets[SourceDatasetType.CMIP6]
        result = calculate_annual_mean_global_mean(input_datasets.path.to_list())
        if "time_bnds" in result:
            result = result.drop_vars("time_bnds")
        result.to_netcdf(definition.output_directory / _OUTPUT_FILENAME)

    def build_execution_result(self, definition: ExecutionDefinition) -> ExecutionResult:
        """Wrap the output file into an :class:`ExecutionResult` with CMEC bundles.

        ``execute`` has already written the output NetCDF file; here we package
        the metadata the REF needs to record the result.
        """
        selectors = definition.datasets[SourceDatasetType.CMIP6].selector_dict()
        input_selectors: dict[str, Any] = {
            "source_id": selectors["source_id"],
            "experiment_id": selectors["experiment_id"],
            "variant_label": selectors["variant_label"],
        }

        return ExecutionResult.build_from_output_bundle(
            definition,
            cmec_output_bundle=CMECOutput.create_template(),
            cmec_metric_bundle=_metric_bundle(input_selectors),
        )


def build_provider() -> DiagnosticProvider:
    """Create the tutorial diagnostic provider and register its diagnostics."""
    provider = DiagnosticProvider("Tutorial", _try_version())
    provider.register(AnnualMeanGlobalMeanTas())
    return provider


#: The tutorial provider, ready to use. Import this in notebook 04.
provider = build_provider()
