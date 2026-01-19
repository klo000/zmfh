"""Policy validation.

Validation is fail-open:
- invalid policy => None

However, *silent* policy failures are a debugging nightmare.

v0.1.3 adds strict top-level key checking:
- unknown keys are treated as invalid policy (and therefore ignored)

Rationale: the most dangerous failure mode is believing a rule is active when
it is actually being ignored.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

from zmfh.policy.model import Policy
from zmfh.runtime.modes import Mode


_KNOWN_KEYS: frozenset[str] = frozenset(
    {
        # Core
        "mode",
        "roots",
        # Governance rules
        "deny",
        "allow",
        # Managed import scanning
        "managed_prefixes",
        "exclude_dirs",
        "max_scan_files",
        # Behavior toggles
        "allow_loose_top_level",
        "raise_on_ambiguous",
        "raise_on_deleted",
        "cache_enabled",
    }
)


def _as_str_list(v: Any) -> Optional[list[str]]:
    if v is None:
        return []
    if isinstance(v, list) and all(isinstance(x, str) for x in v):
        return [x.strip() for x in v if x.strip()]
    return None


def validate_policy_dict_ex(data: Any) -> Tuple[Optional[Policy], list[str]]:
    """Validate a policy JSON object.

    Returns:
        (policy_or_none, errors)
    """

    errors: list[str] = []

    if not isinstance(data, dict):
        return None, ["policy must be a JSON object"]

    # Unknown key detection.
    try:
        unknown = sorted({str(k) for k in data.keys()} - _KNOWN_KEYS)
    except Exception:
        unknown = []
    if unknown:
        errors.append("unknown key(s): " + ", ".join(unknown))

    try:
        mode = Mode.from_text(data.get("mode"))

        deny = _as_str_list(data.get("deny"))
        if deny is None:
            errors.append("deny must be a list of strings")
            deny = []

        allow = _as_str_list(data.get("allow"))
        if allow is None:
            errors.append("allow must be a list of strings")
            allow = []

        managed_prefixes = _as_str_list(data.get("managed_prefixes"))
        if managed_prefixes is None:
            errors.append("managed_prefixes must be a list of strings")
            managed_prefixes = []

        allow_loose_top_level = bool(data.get("allow_loose_top_level", True))
        raise_on_ambiguous = bool(data.get("raise_on_ambiguous", False))
        raise_on_deleted = bool(data.get("raise_on_deleted", True))

        exclude_dirs = _as_str_list(data.get("exclude_dirs"))
        if exclude_dirs is None:
            errors.append("exclude_dirs must be a list of strings")
            exclude_dirs = list(Policy().exclude_dirs)

        roots = _as_str_list(data.get("roots"))
        if roots is None:
            errors.append("roots must be a list of strings")
            roots = []

        max_scan_files = data.get("max_scan_files")
        if max_scan_files is None:
            max_scan_files = Policy().max_scan_files
        if not isinstance(max_scan_files, int) or max_scan_files <= 0:
            errors.append("max_scan_files must be a positive integer")
            max_scan_files = Policy().max_scan_files

        cache_enabled = bool(data.get("cache_enabled", True))

        if errors:
            return None, errors

        return (
            Policy(
                mode=mode,
                deny=deny,
                allow=allow,
                managed_prefixes=managed_prefixes,
                allow_loose_top_level=allow_loose_top_level,
                raise_on_ambiguous=raise_on_ambiguous,
                raise_on_deleted=raise_on_deleted,
                exclude_dirs=exclude_dirs,
                max_scan_files=max_scan_files,
                roots=roots,
                cache_enabled=cache_enabled,
            ),
            [],
        )
    except Exception as e:
        errors.append(f"internal error while validating policy: {e!r}")
        return None, errors


def validate_policy_dict(data: Any) -> Optional[Policy]:
    p, _ = validate_policy_dict_ex(data)
    return p
