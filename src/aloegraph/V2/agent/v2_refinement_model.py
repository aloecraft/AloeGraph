# src/aloegraph/V2/agent/v2_refinement_model.py
"""
v2_refinement_model
===================

- **Module:** `src/aloegraph/V2/agent/v2_refinement_model.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Core state and schema classes for refinement agents in AloeGraph V2.

This module defines the foundational data structures used by refinement
agents to manage iterative improvement workflows. Refinement agents guide
users through cycles of proposing refinements, applying them to items,
and deciding whether to continue, commit, or interrupt the process.

Overview
--------
- **V2Refinement**:
  Represents a single refinement option proposed by the agent. Serves as
  a placeholder schema that can be extended with fields describing the
  refinement type, content, and metadata.

- **V2Refinable**:
  Represents an item subject to refinement (e.g., text, code, or structured
  data). Serves as a placeholder schema that can be extended with fields
  describing the item’s content and refinement history.

- **RefinementAgentState**:
  Extends `V2AloeConfig` to track refinements, refinable items, and
  automation flags. Provides helper methods to check whether refinements
  or items are present.

Responsibilities
----------------
- Provide a consistent schema for refinements and refinable items.
- Track pending refinements and current items during refinement workflows.
- Support automation flags (`auto_request`, `auto_continue`) to control
  agent behavior.
- Serve as the state object passed between refinement agent nodes.

Mermaid Diagram
---------------
```mermaid
flowchart TD
    UserMessage --> State[RefinementAgentState]
    State -->|items| Refinables[V2Refinable]
    State -->|refinements| Refinements[V2Refinement]
    Refinements --> AgentDecision[Refinement Agent]
    AgentDecision -->|apply| Refinables
    AgentDecision -->|commit/continue| State
```    
"""

from aloegraph.V2.v2_base_model import V2AloeConfig
from pydantic import BaseModel, Field


class V2Refinement(BaseModel):
    """
    Represents a single refinement option in AloeGraph V2.

    A refinement is a proposed adjustment or improvement to an artifact
    (such as text, code, or configuration) that the agent can present to
    the user. This class serves as a placeholder schema and can be extended
    with fields describing the refinement type, content, and metadata.
    """
    pass


class V2Refinable(BaseModel):
    """
    Represents an item that can be refined in AloeGraph V2.

    A refinable item is an artifact subject to iterative improvement.
    Examples include draft text, structured data, or configuration objects.
    This class serves as a placeholder schema and can be extended with
    fields describing the item’s content, type, and refinement history.
    """
    pass


class RefinementAgentState(V2AloeConfig):
    """
    State object for refinement agents in AloeGraph V2.

    Extends `V2AloeConfig` to track refinements and refinable items during
    iterative improvement workflows. Used by refinement agents to manage
    pending refinements, current items, and automation flags.

    Attributes
    ----------
    refinements : list[V2Refinement]
        List of pending refinements proposed by the agent.
    items : list[V2Refinable]
        Current list of items subject to refinement.
    auto_request : bool, default False
        Flag indicating whether the agent should automatically request
        refinements without explicit user input.
    auto_continue : bool, default False
        Flag indicating whether the agent should automatically continue
        refinement without waiting for user confirmation.

    Methods
    -------
    hasItems() -> int
        Return the number of refinable items currently tracked.
    hasRefinements() -> int
        Return the number of pending refinements currently tracked.

    Example
    -------
    ```python
    state = RefinementAgentState()
    state.items.append(V2Refinable())
    state.refinements.append(V2Refinement())

    print(state.hasItems())       # 1
    print(state.hasRefinements()) # 1
    ```
    """
    refinements: list[V2Refinement] = Field(
        default_factory=list, description="Pending Refinements")
    items: list[V2Refinable] = Field(
        default_factory=list, description="Current list of refinable items")
    auto_request: bool = Field(default=False, description="")
    auto_continue: bool = Field(default=False, description="")

    def hasItems(self):
        return len(self.items)

    def hasRefinements(self):
        return len(self.refinements)
