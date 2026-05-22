# Climate REF training notebooks

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Climate-REF/climate-ref-tutorials/main?urlpath=lab/tree/notebooks)
[![CI](https://github.com/Climate-REF/climate-ref-tutorials/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/Climate-REF/climate-ref-tutorials/actions/workflows/ci.yaml)

A self-contained set of training notebooks for the
[Climate Rapid Evaluation Framework (REF)](https://climate-ref.org).

The notebooks take you from *what the REF is* through to *querying the public
REF API* and *building a publication-ready figure*.
They are written for climate scientists, analysts, and newcomers with no prior REF knowledge is assumed.

## Run in your browser (no installation)

Click the **launch Binder** badge above.
Binder builds the environment and opens JupyterLab; no local setup is required.

This may take several minutes

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
| 02  | [Querying the REF API](notebooks/02-querying-the-api.ipynb)             | Set up the API client, list diagnostics, fetch metric values, inspect an execution | 01            |
| 03  | [A publication-ready figure](notebooks/03-publication-figure.ipynb)     | Build a polished multi-model metric comparison figure and save it                  | 01, 02        |
| 04  | [Running a diagnostic locally](notebooks/04-local-diagnostic-run.ipynb) | Define a custom diagnostic provider and run it locally on small sample data        | 01            |

More notebooks will be added over time — see [CONTRIBUTING.md](CONTRIBUTING.md).

## How it works

- Notebooks 01–03 query the **live** public REF API at
  <https://api.climate-ref.org>. An internet connection is required; the
  notebooks fail clearly if the API is unreachable.
- The REF API client (`climate_ref_client`) is **generated** from the API's
  [OpenAPI schema](https://api.climate-ref.org/api/v1/openapi.json) by
  `scripts/generate_client.sh`, so it always matches the current API. It is
  not committed to this repository.
- Notebook 04 fetches a small CMIP6 sample dataset via the REF CLI and runs a
  **custom diagnostic provider** — defined in `src/ref_tutorials/provider.py` —
  locally.
- Shared logic lives in the `ref_tutorials` helper package (`src/ref_tutorials`),
  keeping the notebooks short and readable.
- Notebook **outputs are committed** so the notebooks render fully on GitHub
  without being run.

## License

Apache-2.0. See [LICENCE](LICENCE).
