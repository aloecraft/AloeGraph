# src/aloegraph/V2/agent/v2_router_model.py
"""
v2_router_model
===============

- **Module:** `src/aloegraph/V2/agent/v2_router_model.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Routing agent models for AloeGraph V2.

This module defines the state and supporting abstractions for agents that
perform routing decisions within AloeGraph. Routing agents determine whether
a user message should be forwarded to a specific route or handled directly,
and maintain metadata about the routing process.

Overview
--------
- **RouterAgentState**:
  Extends `V2AloeConfig` to include routing metadata. Tracks the chosen
  route (`__ROUTE__`) and optionally references a `parent_state` for
  hierarchical or nested routing scenarios.

- **Integration with AloeGraph**:
  Routing agents are typically implemented as subclasses of `V2AloeGraph`
  with nodes and edges decorated using `@AloeNode` and `@AloeEdge`. They
  use `JSONResponseGeneratorBase` to enforce structured outputs and
  validate routing decisions.

Responsibilities
----------------
- Provide a consistent state object for routing agents.
- Capture both the current route and parent state for context.
- Serve as the foundation for higher‑level router agents that integrate
  with AloeGraph’s execution engine.

Usage
-----
Define a router agent graph that uses `RouterAgentState` to track routing:

```python
class MyRouterGraph(V2AloeGraph[RouterAgentState]):
    @AloeNode(name="Start", is_entry=True)
    def start(self, state: RouterAgentState):
        # Decide route based on user message
        state.__ROUTE__ = "Support"
        state.__EDGE__ = END
        return state
```
"""
from aloegraph.V2.v2_base_model import V2AloeConfig

class RouterAgentState[ParentStateT:V2AloeConfig](V2AloeConfig):
    """
    State object for router agents in AloeGraph V2.

    Extends `V2AloeConfig` to include routing metadata and parent state
    references. Used by router graphs to track the chosen route for a
    user message and maintain context when nested inside larger workflows.

    Attributes
    ----------
    __ROUTE__ : str, optional
        The route selected for the current user message. `None` if no
        route has been determined.
    parent_state : ParentStateT, optional
        Reference to the parent state object. Enables hierarchical or
        nested routing scenarios where the router agent operates within
        a larger graph context.

    Notes
    -----
    - Inherits all fields from `V2AloeConfig` (user message, agent message,
      error message, and control flags).
    - Designed for use in router graphs that decide whether to forward
      messages to specific routes or handle them directly.
    """
    __ROUTE__: str = None
    parent_state: ParentStateT = None
