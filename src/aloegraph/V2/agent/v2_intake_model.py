# src/aloegraph/V2/agent/v2_intake_model.py
"""
v2_intake_model
=====================

- **Module:** `src/aloegraph/V2/agent/v2_intake_model.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

State object for the Intake Agent in AloeGraph V2.

This module defines `IntakeAgentState`, which extends `V2AloeConfig` to
include a routing flag (`should_route`). The Intake Agent uses this state
to triage user messages at the very beginning of the AloeGraph workflow,
deciding whether to respond directly or forward the request to the Router
Agent.

Overview
--------
- **IntakeAgentState**:
  Extends `V2AloeConfig` with:
    * `should_route` — flag indicating whether the message should be
      handed off to the Router Agent (`True`) or handled directly (`False`).

Integration
-----------
- Works in tandem with `IntakeAgentResponse`, which provides the structured
  output for triage decisions.
- Serves as the entry point state for routing workflows in AloeGraph.
- If `should_route=True`, the Router Agent takes over; if `False`, the
  Intake Agent responds directly.

Mermaid Diagram
---------------
```mermaid
flowchart TD
    U[User Message] --> S[IntakeAgentState]
    S -->|should_route=True| R[RouterAgent]
    S -->|should_route=False| M[Direct Intake Reply]
    R --> Downstream[Route Nodes / Tasks]
    M --> End[END]
```
"""

from aloegraph.V2.v2_base_model import V2AloeConfig
from pydantic import Field


class IntakeAgentState(V2AloeConfig):
    """
    State object for the Intake Agent in AloeGraph V2.

    Extends `V2AloeConfig` to include a routing flag that indicates whether
    the user’s message should be forwarded to the Router Agent or handled
    directly by the Intake Agent. This state is used at the very beginning
    of the AloeGraph workflow to triage incoming messages.

    Attributes
    ----------
    should_route : bool, default False
        Flag indicating whether the Intake Agent should forward the user’s
        message to the Router Agent (`True`) or respond directly (`False`).

    Notes
    -----
    - Inherits all fields from `V2AloeConfig` (user message, agent message,
      error message, and control flags).
    - Designed to integrate with `IntakeAgentResponse`, which provides the
      structured output for triage decisions.
    - Acts as the entry point state for routing workflows in AloeGraph.

    Example
    -------
    >>> state = IntakeAgentState(user_message="What is AloeGraph?")
    >>> state.should_route = False
    >>> print(state.user_message)   # "What is AloeGraph?"
    >>> print(state.should_route)   # False
    """
    should_route: bool = Field(default=False, description="")
