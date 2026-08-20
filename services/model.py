"""Backward-compat shim for moved OpenRouterClient.

This module re-exports `OpenRouterClient` from its new location in
`infrastructure.openrouter.client` to avoid breaking imports.
"""

from infrastructure.openrouter.client import OpenRouterClient  # noqa: E402,F401

