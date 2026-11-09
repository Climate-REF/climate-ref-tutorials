# Climate REF training notebooks

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Climate-REF/climate-ref-tutorials/main?urlpath=lab/tree/notebooks)
[![CI](https://github.com/Climate-REF/climate-ref-tutorials/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/Climate-REF/climate-ref-tutorials/actions/workflows/ci.yaml)

A self-contained set of training notebooks for the [Climate Rapid Evaluation Framework (REF)](https://climate-ref.org).

The notebooks take you from *what the REF is* through to *querying public
CMIP7 results* and *building a publication-ready figure*.
They are written for climate scientists, analysts, and newcomers; no prior REF knowledge is assumed.

## Run in your browser (no installation)

Click the **launch Binder** badge above.
Binder builds the environment and opens JupyterLab; no local setup is required.

This may take several minutes

## Run with Docker (pre-built image)

A pre-built JupyterLab image is published to the GitHub Container Registry
on every push to `main` and on every release tag.
No local Python setup is required.

```bash
docker run --rm -p 8888:8888 ghcr.io/climate-ref/climate-ref-tutorials:latest
```

Open the JupyterLab URL printed in the terminal (includes the access token).

## Run locally

Requires [uv](https://docs.astral.sh/uv/), a Python Package Manager to create a local virtual environment.

```bash
git clone https://github.com/Climate-REF/climate-ref-tutorials.git
cd climate-ref-tutorials
uv sync                           # create the environment
uv run bash scripts/generate_client.sh   # generate the REF API client
uv run jupyter lab notebooks      # open the notebooks
```

## Notebooks

The notebooks are designed to be read in order; later ones assume concepts
introduced earlier.

| #   | Notebook                                                                | What you will learn                                                                | Prerequisites |
| --- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------------- |
| 01  | [REF concepts](notebooks/01-ref-concepts.ipynb)                         | The core vocabulary: diagnostics, providers, executions, metrics, datasets         | None          |
| 02  | [Querying the REF API](notebooks/02-querying-the-api.ipynb)             | Fetch metric values, NetCDF data, an ACCESS-ESM1-6 map, and a Taylor diagram       | 01            |
| 03  | [Figure generation](notebooks/03-publication-figure.ipynb)              | Start with ACCESS-ESM1-6, add two model time series, and save the figure            | 01, 02        |
| 04  | [Running a diagnostic locally](notebooks/04-local-diagnostic-run.ipynb) | Run a custom CMIP7 diagnostic on tiny synthetic data generated locally             | 01            |
| 05  | [Multi-diagnostic example](notebooks/05-ecs-temperature-figure.ipynb)   | Join CMIP7 ECS values to historical `tas` series in three figures                   | 01, 02, 03    |

More notebooks will be added over time — see [CONTRIBUTING.md](CONTRIBUTING.md).

## How it works

- Notebooks 01–03 and 05 query the **live** public REF API at <https://api.climate-ref.org>.
  An internet connection is required; the notebooks fail clearly if the API is unreachable.
- The REF API client (`climate_ref_client`) is **generated** from the API's
  [OpenAPI schema](https://api.climate-ref.org/api/v1/openapi.json) by `scripts/generate_client.sh`,
  so it always matches the current API.
  It is not committed to this repository.
- Notebook 04 generates two small synthetic CMIP7-style NetCDF files locally and runs a
  **custom diagnostic provider**, defined in `src/ref_tutorials/provider.py`.
  The synthetic files demonstrate the REF workflow; they are not real model output.
- Shared logic lives in the `ref_tutorials` helper package (`src/ref_tutorials`),
  keeping the notebooks short and readable.
- Notebook **outputs are committed** so the notebooks render fully on GitHub without being run.

## License

Apache-2.0. See [LICENCE](LICENCE).
