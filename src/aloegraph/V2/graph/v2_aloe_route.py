# src/aloegraph/V2/graph/v2_aloe_route.py
"""
v2_aloe_route
===============

- **Module:** `src/aloegraph/V2/graph/v2_aloe_route.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Abstract base class for defining routes in AloeGraph V2.

This module provides `AloeRoute`, the contract for implementing routes
that can be invoked by a `RouterAgent`. A route represents a sub‑graph
or workflow that handles a specific type of user message. Each route
must describe itself, indicate availability, and manage its internal
state. Routes are parameterized by a parent state type and their own
state type, both extending `V2AloeConfig`.

Overview
--------
- **AloeRoute**:
  Abstract base class requiring implementations of:
    * `describeRoute(parent_state)` — human‑readable description of the route.
    * `isAvailable(parent_state)` — whether the route can be invoked.
    * `getRouteState(parent_state)` — retrieve the route’s internal state.
    * `setRouteState(parent_state, state)` — update the parent state with
      results from the route.

Integration
-----------
Routes are registered with a `RouterAgent` via `addRoute`. The agent
uses `describeRoute` and `isAvailable` to present options to the user
and decide whether to invoke a route. When invoked, the route’s state
is propagated back into the parent state.

Mermaid Diagram
---------------
```mermaid
flowchart TD
    RA[RouterAgent] -->|addRoute| AR[AloeRoute]
    AR -->|describeRoute| Prompt[Routing Prompt]
    AR -->|isAvailable| Decision[Availability Check]
    AR -->|getRouteState| RS[Route State]
    AR -->|setRouteState| PS[Parent State Updated]
```    
"""

from aloegraph.V2.v2_aloe_graph import V2AloeGraph
from aloegraph.V2.v2_base_model import V2AloeConfig

from abc import ABC, abstractmethod

class AloeRoute[ParentStateT:V2AloeConfig, StateT:V2AloeConfig](ABC):
    """
    Abstract base class for defining routes in AloeGraph V2.

    A route represents a sub‑graph or workflow that can be invoked by a
    `RouterAgent`. Each route must implement methods to describe itself,
    determine availability, and manage its internal state. Routes are
    parameterized by a parent state type (`ParentStateT`) and their own
    state type (`StateT`), both extending `V2AloeConfig`.

    Responsibilities
    ----------------
    - Provide a human‑readable description of the route for display in
      routing prompts (`describeRoute`).
    - Indicate whether the route is currently available for invocation
      (`isAvailable`).
    - Expose and manage the route’s internal state (`getRouteState`,
      `setRouteState`).
    - Integrate seamlessly with `V2AloeGraph` so routes can be compiled,
      executed, and visualized like any other graph.

    Attributes
    ----------
    RouteName : str
        The name of the route. Defaults to the class name if not explicitly
        set during initialization.
    GraphName : str
        The graph identifier for visualization and debugging (inherited
        from `V2AloeGraph` when implemented).

    Abstract Methods
    ----------------
    describeRoute(parent_state: ParentStateT) -> str
        Return a human‑readable description of the route given the parent
        state context.
    isAvailable(parent_state: ParentStateT) -> bool
        Return True if the route can be invoked in the current context.
    getRouteState(parent_state: ParentStateT) -> V2AloeConfig
        Retrieve the route’s internal state object.
    setRouteState(parent_state: ParentStateT, state: StateT) -> V2AloeConfig
        Update the parent state with the results of executing the route.

    Example
    -------
    ```python
    class SupportRoute(AloeRoute[V2AloeConfig, V2AloeConfig], V2AloeGraph[V2AloeConfig]):
        def describeRoute(self, parent_state):
            return "Handles customer support inquiries."

        def isAvailable(self, parent_state):
            return parent_state.user_message and "support" in parent_state.user_message.lower()

        def getRouteState(self, parent_state):
            return V2AloeConfig(user_message=parent_state.user_message)

        def setRouteState(self, parent_state, state):
            parent_state.agent_message = state.agent_message
            return parent_state
    ```
    """
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        bases = getattr(cls, "__orig_bases__", [])
        route_args = None
        graph_args = None
        for b in bases:
            if getattr(b, "__origin__", None) is AloeRoute:
                route_args = b.__args__
            if getattr(b, "__origin__", None) is V2AloeGraph:
                graph_args = b.__args__

        # FIXEME: Type checks weird polymorphism handling
        # if not graph_args:
        #     raise TypeError(f"{cls.__name__}: AloeRoute must also implement V2AloeGraph")

        # if route_args and graph_args and route_args[0] is not graph_args[0]:
        #     raise TypeError(f"{cls.__name__}: StateT mismatch between AloeRoute and V2AloeGraph")

        original_init = cls.__init__

        def wrapped_init(self, *args, **kwargs):
            if not hasattr(self, "RouteName"):
                self.RouteName = cls.__name__
            if callable(original_init):
                original_init(self, *args, **kwargs)
        cls.__init__ = wrapped_init

    @abstractmethod
    def describeRoute(self, parent_state: ParentStateT) -> str:
        """
        FIXME-MIKE: API docstring is not totally accurate. These methods are read by the router agent to determine how to route requests from intake agent
        """
        pass

    @abstractmethod
    def isAvailable(self, parent_state: ParentStateT) -> bool:
        """
        FIXME-MIKE: API docstring is not totally accurate. These methods are read by the router agent to determine how to route requests from intake agent
        """
        pass

    @abstractmethod
    def getRouteState(self, parent_state: ParentStateT) -> V2AloeConfig:
        pass

    @abstractmethod
    def setRouteState(self, parent_state: ParentStateT, state: StateT) -> V2AloeConfig:
        pass
