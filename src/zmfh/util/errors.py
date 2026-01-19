"""Internal error types."""

from __future__ import annotations


class ZMFHError(Exception):
    """Base error."""


class PolicyError(ZMFHError):
    pass


class RegistryError(ZMFHError):
    pass
