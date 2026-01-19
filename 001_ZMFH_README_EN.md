# ZMFH Project README

ZMFH is an **upper-language layer** that replaces and extends Python’s import behavior.
Without changing Python syntax, it redefines import/execution/module access as **policy and contract**.

## 1) Purpose

ZMFH has one goal:

> Make developers stop thinking about imports.

ZMFH does not create a new language.
It fills the structural gap Python intentionally leaves open.

## 2) Problem

Limits of the default Python import model:

- Import success/failure depends on where you run the program.
- Relative vs absolute imports are not intuitive at scale.
- `sys.path` mutation becomes a “common practice.”
- As projects grow, the cost of explaining structure explodes.
- Failures are often hard to diagnose quickly.

This is not a “skill issue.”
It’s a structural governance gap.

## 3) Core Principles

1. **Zero intrusion into existing code**
   - No rewriting required
   - Keep normal Python import syntax

2. **Works without mandatory configuration**
   - No forced config files
   - No reliance on `__init__.py` or `sys.path` hacks

3. **Filename-based recognition**
   - Filenames act as identifiers
   - Meaning > location

4. **Policy-based allowance**
   - Import is a permission, not a freedom
   - Central policy decides allow/deny

5. **Deterministic failures**
   - Failures return clear, decisive reasons
   - No silent success, no “maybe”

## 4) What ZMFH Is

ZMFH is not a library.
ZMFH is not a framework.

ZMFH is an **upper-language layer** on top of Python:

- Syntax: Python
- Semantics: ZMFH
- Execution order: ZMFH
- Import governance: ZMFH

User experience:

> “It’s Python syntax, but you can’t do random stuff.”

## 5) Conceptual Architecture

- **Global Index**: index project-wide modules; key-based access (not path-based)
- **Registry**: tracks known modules; can recognize legacy code at import time
- **Policy Layer**: defines allow/deny; supports org/department/project scopes
- **Resolver**: interprets import requests independent of execution location
- **Evidence / Log**: records all import attempts for audit/debug/reproducibility

## 6) Nested Layers (Scalability)

ZMFH supports **layered nesting**:

- Org ZMFH
  - Department ZMFH
    - Team ZMFH
      - Project ZMFH

Each layer owns its own policy.
Upper layers enforce boundaries; lower layers keep autonomy.

## 7) Expected Outcomes

- Eliminates import-related incidents
- Cuts structural explanation cost dramatically
- Reduces productivity gap between junior and senior devs
- Shifts code review focus to architecture (not import trivia)
- Enables long-lived, large-scale Python systems

This is not “nice to have.”
At scale, it becomes infrastructure.

## 8) Positioning

ZMFH does not replace Python.
ZMFH does not break the Python ecosystem.

ZMFH lets Python enter domains where Python previously failed at scale.

**A survival layer for Python at large scale.**

## 9) Project Status

- Born from real-world pain in large projects
- Validated inside the ALP project
- Being separated as an independent open project

## 10) One-line Summary

ZMFH frees imports from syntax and lifts them into **governance and contracts**—an upper-language layer for Python.
