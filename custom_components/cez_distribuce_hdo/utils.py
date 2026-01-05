"""Utility functions for CEZ Distribution HDO integration."""

from __future__ import annotations

from .const import (
    DEFAULT_PREFIX,
)


def object_prefix(prefix: str, signal: str, split: str = " ") -> str:
    """Return base object_id prefix: 'hdo<split><signal>' or '<prefix><split><signal>'."""
    return f"{prefix}{split}{signal}" if prefix else f"{DEFAULT_PREFIX}{split}{signal}"
