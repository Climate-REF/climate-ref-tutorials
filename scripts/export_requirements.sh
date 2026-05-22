#!/usr/bin/env bash
# Regenerate .binder/requirements.txt from the resolved uv environment.
#
# Binder/repo2docker installs from requirements.txt; uv is the source of
# truth locally. Run this after changing dependencies in pyproject.toml.
# CI checks that the committed file is up to date.
set -euo pipefail

cd "$(dirname "$0")/.."

uv export --no-hashes --no-emit-project --format requirements-txt \
    >.binder/requirements.txt

echo "Wrote .binder/requirements.txt"
