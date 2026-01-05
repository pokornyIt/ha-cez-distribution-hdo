"""Utility functions for CEZ Distribution HDO integration."""

from __future__ import annotations

import logging
from homeassistant.util import slugify

from .const import (
    DEFAULT_PREFIX,
)

_LOGGER = logging.getLogger(__name__)


def object_prefix(prefix: str, signal: str, split: str = " ") -> str:
    """Return base object_id prefix: 'hdo<split><signal>' or '<prefix><split><signal>'."""
    # sig = sanitize_signal_for_entity(
    #     signal
    # )  # e.g., 'čez' -> 'cez', 'tariff-1' -> 'tariff_1'
    if prefix:
        return f"{slugify(prefix)}{split}{signal}"
    return f"{DEFAULT_PREFIX}{split}{signal}"
