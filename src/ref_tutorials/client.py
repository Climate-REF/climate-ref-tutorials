"""Construction of the REF API client.

The client class lives in ``climate_ref_client``, a package that is
*generated* from the REF API's OpenAPI schema (see ``scripts/generate_client.sh``).
The import is deliberately deferred to the function body so that the rest of
this package -- and its tests -- can be used without the generated client
being present.
"""

from __future__ import annotations

from typing import Any

#: Public, read-only REF API used throughout the training notebooks.
DEFAULT_API_URL = "https://api.climate-ref.org"


def get_client(base_url: str = DEFAULT_API_URL) -> Any:
    """Return a REF API client pointed at ``base_url``.

    Parameters
    ----------
    base_url
        Root URL of the REF API. Defaults to the public service.

    Returns
    -------
    climate_ref_client.Client
        A client ready to pass to the ``climate_ref_client`` API functions.

    Raises
    ------
    ModuleNotFoundError
        If the generated ``climate_ref_client`` package is not installed.
        Run ``scripts/generate_client.sh`` (the Binder/CI setup does this
        automatically).
    """
    try:
        from climate_ref_client import Client
    except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
        msg = (
            "The generated 'climate_ref_client' package is not installed. "
            "Run scripts/generate_client.sh to generate and install it."
        )
        raise ModuleNotFoundError(msg) from exc

    return Client(base_url)
