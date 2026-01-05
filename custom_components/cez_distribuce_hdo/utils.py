"""Utility functions for CEZ Distribution HDO integration."""

from __future__ import annotations

import logging
from homeassistant.util import slugify

from .const import (
    DEFAULT_PREFIX,
)

from cez_distribution_hdo import (
    sanitize_signal_for_entity,
)

_LOGGER = logging.getLogger(__name__)


def object_prefix(prefix: str, signal: str, split: str = "_") -> str:
    """Return base object_id prefix: 'hdo<split><signal>' or '<prefix><split><signal>'."""
    sig = sanitize_signal_for_entity(
        signal
    )  # e.g., 'čez' -> 'cez', 'tariff-1' -> 'tariff_1'
    if prefix:
        return f"{slugify(prefix)}{split}{sig}"
    return f"{DEFAULT_PREFIX}{split}{sig}"
