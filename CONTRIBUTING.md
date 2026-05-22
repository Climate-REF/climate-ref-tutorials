# Contributing

Thanks for helping improve the Climate REF training notebooks.

## Adding a notebook

The notebook set is designed to grow. To add one:

1. **Pick the next number.** Notebooks use a two-digit prefix
   (`05-your-topic.ipynb`) in `notebooks/`. The number defines reading order.
2. **Write the notebook.** Keep it focused on a single learning goal. State
   prerequisites in the first markdown cell. Reuse the `ref_tutorials` helper
   package rather than repeating client/plotting boilerplate — if you find
   yourself copying code between notebooks, add a helper instead.
3. **Add an index row.** Add the notebook to the table in `README.md`.
4. **Leave outputs in.** Notebook outputs are intentionally committed so the
   notebooks render on GitHub. Run the notebook top-to-bottom before
   committing so the saved outputs are current.
5. **Check it passes CI** (below).

## The `ref_tutorials` helper package

Shared logic lives in `src/ref_tutorials`. It has a deliberately small, stable
interface. New helpers should be pure and testable where possible — add a unit
test in `tests/` for any non-trivial logic.

## Running checks locally

```bash
uv sync --extra dev

# Lint
uv run ruff check src tests
uv run nbqa ruff notebooks

# Unit tests for the helper package
uv run pytest tests

# Execute every notebook end-to-end (needs the generated client + internet)
uv run bash scripts/generate_client.sh
uv run pytest --nbmake notebooks
```

## Dependencies

`pyproject.toml` is the source of truth, managed with `uv`. After changing
dependencies, regenerate the Binder requirements file:

```bash
bash scripts/export_requirements.sh
```

CI fails if `.binder/requirements.txt` is out of sync.

## CI

Every pull request runs three jobs: lint, helper-package unit tests, and full
notebook execution. A weekly scheduled run catches drift against the live REF
API even when the repo is idle.
