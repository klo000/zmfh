
# Changelog

This project follows semantic versioning.

## 1.0.0

- Stable auto-apply bootstrap via `sitecustomize` and `.pth` autoboot.
- Fail-open safety contract: ZMFH must never brick Python or user projects.
- Policy system (JSON) with strict validation (unknown keys invalidate policy).
- Enforce/strict mode: `deny` rules actively block imports (including installed modules).
- Managed import scanning under configured roots and clear deletion diagnostics when a previously resolvable module vanishes.
- CLI utilities: `zmfh doctor`, `zmfh status`, `zmfh policy ...`, `zmfh trace`, `zmfh selftest`.

