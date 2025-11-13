# src/aloegraph/V2/exception/base_exceptions.py
"""
base_exceptions
=================

- **Module:** `src/aloecraft/V2/exception/base_exceptions.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Custom exception types for AloeGraph V2 compilation errors.

This module defines the base exception `AloeGraphCompileError` and its
specialized subclass `AloeRouteCompileError`. These exceptions are raised
when graph or route compilation fails due to invalid configuration,
missing dependencies, or type mismatches.

Overview
--------
- **AloeGraphCompileError**:
  Base exception for all compile‑time errors in AloeGraph. Raised when
  a graph fails to compile due to structural or configuration issues.

- **AloeRouteCompileError**:
  Specialized exception for route compilation errors. Raised when a route
  fails to compile due to type mismatches, missing integration with
  `V2AloeGraph`, or other route‑specific problems.

Integration
-----------
- Used by agent and graph classes during `compile()` and `preflight()`
  checks to enforce correctness.
- Ensures contributors receive clear, descriptive error messages when
  compilation fails.
- Provides a consistent error hierarchy for handling graph and route
  failures separately.

Usage
-----
```python
from aloegraph.V2.exception.v2_compile_errors import (
    AloeGraphCompileError,
    AloeRouteCompileError
)

# Example: raise a general graph compile error
raise AloeGraphCompileError("Graph failed to compile: missing node definition")

# Example: raise a route compile error
raise AloeRouteCompileError("Route failed to compile: state mismatch")
```
"""

class AloeGraphCompileError(Exception):
    """
    Base exception for AloeGraph compilation errors.

    Raised when a graph fails to compile due to invalid configuration,
    missing dependencies, or other structural issues. This serves as the
    root exception type for all compile‑time errors in AloeGraph.

    Attributes
    ----------
    message : str
        Human‑readable description of the compilation error.

    Example
    -------
    ```python
    raise AloeGraphCompileError("Graph failed to compile: missing node definition")
    ```
    """    
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

class AloeRouteCompileError(AloeGraphCompileError):
    """
    Exception for AloeGraph route compilation errors.

    Raised when a route fails to compile due to invalid configuration,
    type mismatches, or missing integration with `V2AloeGraph`. Inherits
    from `AloeGraphCompileError` to provide more specific context for
    route‑related failures.

    Attributes
    ----------
    message : str
        Human‑readable description of the route compilation error.

    Example
    -------
    ```python
    raise AloeRouteCompileError("Route failed to compile: state mismatch")
    ```
    """    
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)