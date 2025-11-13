# src/aloegraph/V2/agent/v2_intake_agent.py
"""
v2_intake_agent
===============

- **Module:** `src/aloegraph/V2/agent/v2_intake_agent.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Graph implementation of the Intake Agent in AloeGraph V2.

This module defines `IntakeAgent`, a specialized `V2AloeGraph` that serves
as the entry point for AloeGraph workflows. The Intake Agent’s role is
triage: it reads the user’s latest message, decides whether to respond
directly or forward the request to the Router Agent, and updates the
intake state accordingly.

Overview
--------
- **IntakeAgent**:
  A graph that:
    * Defines the entry node `ProcessUserRequest`, which evaluates the
      user’s message and produces an `IntakeAgentResponse`.
    * Updates the `IntakeAgentState` with routing decisions (`should_route`)
      and direct replies (`agent_message`).
    * Integrates with a `JSONResponseGeneratorBase[IntakeAgentResponse]`
      to enforce structured outputs and schema validation.

Integration
-----------
- Works in tandem with:
    * `IntakeAgentState` — holds the routing flag and user/agent messages.
    * `IntakeAgentResponse` — structured output schema for triage decisions.
- Serves as the first stage in the AloeGraph pipeline before the Router Agent.
- If `should_route=True`, the Router Agent takes over; if `False`, the
  Intake Agent responds directly.

Mermaid Diagram
---------------
```mermaid
flowchart TD
    U[User Message] --> I[IntakeAgent.ProcessUserRequest]
    I --> R[RouterAgent]:::route
    I --> M[Direct Intake Reply]:::direct
    R --> Downstream[Route Nodes / Tasks]
    M --> End[END]

    classDef route fill=#f9f,stroke=#333,stroke-width=1px;
    classDef direct fill=#bbf,stroke=#333,stroke-width=1px;
```
"""

from aloegraph.V2.graph.v2_aloe_node import AloeNode, AloeEdge
from aloegraph.V2.v2_aloe_graph import V2AloeGraph
from aloegraph.V2.v2_base_model import END
from aloegraph.V2.response_generator import JSONResponseGeneratorBase
import aloegraph.V2.agent.v2_intake_model as v2_intake_model
import aloegraph.V2.agent.v2_intake_response as v2_intake_response


class IntakeAgent(V2AloeGraph[v2_intake_model.IntakeAgentState]):
    """
    Intake agent graph for AloeGraph V2.

    The Intake Agent is the entry point of the AloeGraph workflow. Its role
    is triage: it reads the user’s latest message, decides whether to respond
    directly or forward the request to the Router Agent, and updates the
    intake state accordingly. This ensures that system‑level questions are
    answered immediately, while task‑oriented requests are routed downstream.

    Responsibilities
    ----------------
    - Define the entry node (`ProcessUserRequest`) that evaluates the user’s
      message and produces an `IntakeAgentResponse`.
    - Update the `IntakeAgentState` with:
        * `should_route` — whether to forward the message to the Router Agent.
        * `agent_message` — direct reply to the user if routing is not required.
    - Integrate with a `JSONResponseGeneratorBase[IntakeAgentResponse]` to
      enforce structured outputs and schema validation.
    - Serve as the first stage in the AloeGraph pipeline before routing.

    Attributes
    ----------
    state : IntakeAgentState
        The current intake state, including user message, agent message,
        and routing flag.
    response_generator : JSONResponseGeneratorBase[IntakeAgentResponse]
        Generator used to produce structured intake responses.

    Methods
    -------
    ProcessUserRequest(state) -> IntakeAgentState
        Entry node that processes the user’s message, generates a response,
        and updates the intake state with routing decisions.

    Example
    -------
    ```python
    from aloegraph.V2.agent.v2_intake_model import IntakeAgentState
    from aloegraph.V2.agent.v2_intake_response import IntakeAgentResponse
    from aloegraph.V2.response_generator import GeminiJSONResponseGenerator

    # Initialize intake agent
    initial_state = IntakeAgentState(user_message="What is AloeGraph?")
    response_gen = GeminiJSONResponseGenerator[IntakeAgentResponse](
        client, "IntakeAgent", "Handles triage of user requests"
    )
    agent = IntakeAgent(initial_state, response_gen)

    # Compile and run intake workflow
    agent.compile()
    final_state = agent.invoke(initial_state)

    print(final_state.should_route)   # False (direct response)
    print(final_state.agent_message)  # "AloeGraph is ..."
    ```
    """

    @AloeNode(is_entry=True)
    @AloeEdge(target=END)
    def ProcessUserRequest(self, state: v2_intake_model.IntakeAgentState) -> v2_intake_model.IntakeAgentState:
        response = self.response_generator.generate(state.user_message)
        state.should_route = response.should_route
        state.agent_message = response.agent_message
        state.__EDGE__ = END
        return state

    def __init__(self, initial_state: v2_intake_model.IntakeAgentState, response_generator: JSONResponseGeneratorBase[v2_intake_response.IntakeAgentResponse]):
        self.state = initial_state
        self.response_generator = response_generator
