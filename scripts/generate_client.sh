#!/usr/bin/env bash
# Generate and install the REF API client from the live OpenAPI schema.
#
# The client is generated rather than committed so it always matches the current API. 
# This script is run by the Binder build (.binder/postBuild), by CI, and can be run manually after `uv sync`.
set -euo pipefail

API_SCHEMA_URL="${REF_API_SCHEMA_URL:-https://api.climate-ref.org/api/v1/openapi.json}"
OUTPUT_DIR="${REF_CLIENT_OUTPUT_DIR:-climate_ref_client}"
CONFIG_FILE="$(mktemp -t openapi-client-config.XXXXXX.yaml)"

# Pin the generated package/import name so notebook imports stay stable
# even if the API's OpenAPI `info.title` is renamed upstream.
cat >"$CONFIG_FILE" <<'YAML'
package_name_override: climate_ref_client
project_name_override: climate-ref-client
YAML

echo "Generating REF API client from ${API_SCHEMA_URL}"
uvx --quiet --from openapi-python-client openapi-python-client generate \
    --url "$API_SCHEMA_URL" \
    --config "$CONFIG_FILE" \
    --meta setup \
    --output-path "$OUTPUT_DIR" \
    --overwrite

echo "Installing generated client from ./${OUTPUT_DIR}"
python -m pip install --quiet "./${OUTPUT_DIR}"

echo "Done. 'import climate_ref_client' is now available."
