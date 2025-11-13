# src/aloegraph/V2/agent/v2_router_agent.py
"""
v2_router_agent
===============

- **Module:** `src/aloegraph/V2/agent/v2_router_model.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Routing agent graph implementation for AloeGraph V2.

This module defines `RouterAgent`, a specialized graph that decides whether
a user message should be routed to one of several available sub‑graphs
(`AloeRoute`) or handled directly. It extends `V2AloeGraph` with routing
logic, integrates with structured response generators, and manages route
registration and invocation.

Overview
--------
- **RouterAgent**:
  A graph that:
    * Defines entry and routing nodes (`decide_can_route_request`, `invoke_route`)
      using `@AloeNode` and `@AloeEdge`.
    * Uses a `JSONResponseGeneratorBase[RouterAgentResponse]` to generate
      validated routing decisions.
    * Tracks available routes and ensures they are compiled before execution.
    * Invokes selected routes, propagates state, and handles interrupts or
      resumes in the routing flow.

- **Integration**:
  Routes are defined as `AloeRoute` instances and registered with the agent
  via `addRoute`. The agent can query available routes for a given parent
  state using `getAvailableRoute`.

Responsibilities
----------------
- Provide a consistent routing mechanism within AloeGraph workflows.
- Enforce structured outputs via Pydantic response schemas.
- Support nested or hierarchical routing by referencing parent states.
- Handle interrupts (`__INTERRUPT__`) and resumes (`__RESUME__`) gracefully
  during route invocation.

Usage
-----
```python
from aloegraph.V2.agent.v2_router_model import RouterAgentState, RouterAgent
from aloegraph.V2.agent.v2_router_response import RouterAgentResponse
from aloegraph.V2.response_generator import GeminiJSONResponseGenerator

# Initialize router agent
initial_state = RouterAgentState()
response_gen = GeminiJSONResponseGenerator[RouterAgentResponse](
    client, "RouterAgent", "Routes user messages"
)
router = RouterAgent(initial_state, response_gen)

# Add routes
router.addRoute(SupportRoute(), "Support")
router.addRoute(SalesRoute(), "Sales")

# Compile and invoke
router.compile()
final_state = router.invoke(initial_state)
```
"""

import aloegraph.V2.agent.v2_router_model as v2_router_model
import aloegraph.V2.agent.v2_router_response as v2_router_response
import aloegraph.V2.v2_base_model as v2_base_model
from aloegraph.V2.v2_base_model import END
from aloegraph.V2.graph.v2_aloe_node import AloeNode, AloeEdge
from aloegraph.V2.graph.v2_aloe_route import AloeRoute
from aloegraph.V2.v2_aloe_graph import V2AloeGraph
from aloegraph.V2.v2_base_model import V2AloeConfig
from aloegraph.V2.response_generator import JSONResponseGeneratorBase

from typing import Union


class RouterAgent[ParentStateT:V2AloeConfig](V2AloeGraph[v2_router_model.RouterAgentState[ParentStateT]]):
    """
    Router agent graph for AloeGraph V2.

    `RouterAgent` extends `V2AloeGraph` to implement routing logic that
    decides whether a user message should be forwarded to a specific route
    or handled directly. It manages available routes, invokes them when
    appropriate, and integrates with a response generator to enforce
    structured outputs.

    Responsibilities
    ----------------
    - Define entry and routing nodes (`decide_can_route_request`, `invoke_route`)
      using `@AloeNode` and `@AloeEdge` decorators.
    - Generate routing decisions via a `JSONResponseGeneratorBase` that
      produces validated `RouterAgentResponse` objects.
    - Track available routes and their initialization state.
    - Invoke selected routes, propagate user messages, and handle interrupts
      or resumes in the routing flow.
    - Perform preflight checks to ensure all routes are compiled before
      execution.

    Attributes
    ----------
    state : RouterAgentState
        The current routing state, including user message, agent message,
        and routing metadata.
    routes : dict[str, AloeRoute]
        Mapping of route names to `AloeRoute` instances managed by this agent.
    response_generator : JSONResponseGeneratorBase[RouterAgentResponse]
        Generator used to produce structured routing decisions.

    Methods
    -------
    decide_can_route_request(state) -> RouterAgentState
        Entry node that evaluates available routes and decides whether to
        forward the message or respond directly.
    invoke_route(state) -> RouterAgentState
        Node that invokes the selected route, propagates state, and handles
        interrupts or resumes.
    preflight() -> bool
        Ensures all routes are compiled before graph execution.
    addRoute(routeAgent, routeName)
        Register a new route with the agent.
    getAvailableRoute(parent_state, route_name=None) -> Union[list[AloeRoute], AloeRoute]
        Retrieve available routes for the given parent state, or a specific
        route by name.

    Example
    -------
    ```python
    from aloegraph.V2.agent.v2_router_model import RouterAgentState
    from aloegraph.V2.agent.v2_router_response import RouterAgentResponse
    from aloegraph.V2.response_generator import GeminiJSONResponseGenerator

    # Initialize router agent
    initial_state = RouterAgentState()
    response_gen = GeminiJSONResponseGenerator[RouterAgentResponse](client, "RouterAgent", "Routes user messages")
    router = RouterAgent(initial_state, response_gen)

    # Add routes
    router.addRoute(MySupportRoute(), "Support")
    router.addRoute(MySalesRoute(), "Sales")

    # Compile and invoke
    router.compile()
    final_state = router.invoke(initial_state)
    ```
    """

    @AloeNode(is_entry=True, node_render_shape=v2_base_model.NodeRenderShape.DIAMOND)
    @AloeEdge(target="invoke_route")
    @AloeEdge(target=END)
    def decide_can_route_request(self, state: v2_router_model.RouterAgentState) -> v2_router_model.RouterAgentState:
        route_descriptions = "\n".join(
            [f"- {route.RouteName}: {route.describeRoute(state.parent_state)}" for route in self.getAvailableRoute(parent_state=state.parent_state)])
        prompt = f"""
user_message: {state.user_message}

available routes:
---
{route_descriptions}
"""
        response: v2_router_response.RouterAgentResponse =\
            self.response_generator.generate(prompt)

        # self.notify_log(prompt)
        # self.notify_log("")
        # self.notify_log(f"response:\n---\n{response}")
        # self.notify_log(f"")
        # self.notify_log(f"Available Routes:\n---\n{self.getAvailableRoute(state.parent_state)}")
        # self.notify_log(f"")
        # self.notify_log(f"Checking Intended:\n---\n{self.getAvailableRoute(state.parent_state, response.route)}")
        # self.notify_log(f"")
        # self.notify_log(f"route_name: {response.route}\nself.routes:{self.routes}\n")

        if response.should_route and self.getAvailableRoute(state.parent_state, response.route):
            state.__ROUTE__ = response.route
            state.__EDGE__ = "invoke_route"
        else:
            state.agent_message = response.agent_message
            state.__EDGE__ = END
        return state

    @AloeNode(node_render_shape=v2_base_model.NodeRenderShape.CIRCLE)
    @AloeEdge(target="invoke_route", interrupt=True)
    @AloeEdge(target=END)
    def invoke_route(self, state: v2_router_model.RouterAgentState) -> v2_router_model.RouterAgentState:
        if state.__RESUME__:
            if self.getAvailableRoute(state.parent_state, state.__RESUME__):
                self.notify_log(
                    f"invoke_route - __RESUME__ Requested: {state.__RESUME__}")
                state.__ROUTE__ = state.__RESUME__
                state.__RESUME__ = ""
            else:
                self.notify_log(
                    f"invoke_route - __RESUME__ Requested: {state.__RESUME__} (NOT AVAILABLE)")
        route = self.routes[state.__ROUTE__]
        route_state = route.getRouteState(state.parent_state)
        route_state.user_message = state.user_message
        # --- Invoking Route ---
        route_state = route.setRouteState(
            state.parent_state, route.invoke(route_state))
        state.agent_message = route_state.agent_message
        if route_state.__INTERRUPT__:
            self.notify_log(
                f"invoke_route - __INTERRUPT__ Received: {state.__INTERRUPT__} (NOT AVAILABLE)")
            state.__RESUME__ = state.__ROUTE__
            state.__EDGE__ = "invoke_route"
        else:
            state.__EDGE__ = END
        return state

    def preflight(self) -> bool:
        for route_name, aloe_route in self.routes.items():
            if not aloe_route._is_initialized:
                aloe_route.compile(route_name, log_notifier=self.log_notifier)
        return super().preflight()

    def __init__(self, initial_state: v2_router_model.RouterAgentState, response_generator: JSONResponseGeneratorBase[v2_router_response.RouterAgentResponse]):
        self.state = initial_state
        self.routes: dict[str, AloeRoute] = {}
        self.response_generator: JSONResponseGeneratorBase[
            v2_router_response.RouterAgentResponse] = response_generator

    def addRoute(self, routeAgent: AloeRoute, routeName: str):
        self._is_initialized = False
        routeAgent.RouteName = routeName
        routeAgent.GraphName = routeName
        self.routes[routeName] = routeAgent

    def getAvailableRoute(self, parent_state: ParentStateT, route_name: str = None) -> Union[list[AloeRoute], AloeRoute]:
        if route_name:
            if route_name in self.routes:
                return self.routes[route_name]
            else:
                return None
        else:
            return [r for r in self.routes.values() if r.isAvailable(parent_state)]
