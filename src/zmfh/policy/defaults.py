"""Default policy."""

from __future__ import annotations

from zmfh.policy.model import Policy


def default_policy() -> Policy:
    return Policy()
