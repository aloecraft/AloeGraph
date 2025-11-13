# src/aloegraph/V2/agent/v2_router_response.py
"""
v2_router_response
==========================

- **Module:** `src/aloegraph/V2/agent/v2_router_response.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Defines the response schema for the Router Agent in AloeGraph V2.

This module provides `RouterAgentResponse`, a specialized extension of
`BaseResponse` that captures routing decisions made by an agent. It is
used when a system needs to determine whether a user message should be
forwarded to another route or handled directly by the agent.

Overview
--------
- **RouterAgentResponse**:
  Extends `BaseResponse` with fields for:
    * `route` — the chosen route for the user message
    * `should_route` — flag indicating whether routing should occur
    * `agent_message` — direct reply to the user if no routing is performed

- **SYSTEM_INSTRUCTION**:
  Classmethod that constructs the system prompt for the Router Agent,
  guiding it to select an appropriate route or respond directly. The
  prompt includes the JSON schema for validation.

Responsibilities
----------------
- Provide a consistent schema for routing decisions.
- Enforce structured outputs via Pydantic validation.
- Supply system instructions that ensure the agent produces predictable
  JSON responses.

Usage
-----
Subclass or use `RouterAgentResponse` in conjunction with a response
generator to validate routing outputs:

```python
from aloegraph.V2.router_agent_response import RouterAgentResponse

response = RouterAgentResponse(
    route="Support",
    should_route=True,
    agent_message=""
)

if response.should_route:
    print(f"Routing to: {response.route}")
else:
    print(f"Agent reply: {response.agent_message}")
```    
"""

from aloegraph.V2.v2_base_response import BaseResponse

from pydantic import Field
import json

class RouterAgentResponse(BaseResponse):
    """
    Response schema for the Router Agent in AloeGraph V2.

    This model extends `BaseResponse` to capture routing decisions made
    by a specialized agent. It determines whether a user message should
    be forwarded to another route or handled directly, and provides the
    appropriate metadata and agent message.

    Attributes
    ----------
    route : str, optional
        The most appropriate route for the user message, chosen from the
        list of available routes. `None` if no route is selected.
    should_route : bool, default False
        Flag indicating whether the message should be routed. If True,
        the `route` field must contain the target route. If False, the
        agent will respond directly and `agent_message` will be used.
    agent_message : str
        Direct response to the user if `should_route` is False. Ignored
        when `should_route` is True.

    Class Methods
    -------------
    SYSTEM_INSTRUCTION(agent_name, agent_description) -> str
        Construct the system prompt for the Router Agent. This prompt
        guides the agent to select an appropriate route or respond
        directly, and includes the JSON schema for validation.

    Example
    -------
    ``` python
    response = RouterAgentResponse(
        route="Support",
        should_route=True,
        agent_message=""
    )
    print(response.should_route)  # True
    print(response.route)         # "Support"
    ```
    """
    route: str = Field(
        default=None, description="Most appropriate route (if any) for the user message from the list of available routes")
    should_route: bool = Field(
        default=False, description="True if an appropriate route for the user message has been determined in the \"route\" field, else False")
    agent_message: str = Field(
        default=False, description="Direct response to user if user message will not be routed by setting \"should_route\" to False. This value will be ignored if \"should_route\" is True")

    @classmethod
    def SYSTEM_INSTRUCTION(cls, agent_name: str, agent_description: str):
        return f"""
You are the Router Agent for {agent_name}.

**What is {agent_name}?**

> {agent_description}

**Current Task**
- Your role is to choose an appropriate route for the user message from the list of available routes
- Read the user’s latest message.

**Guidelines:**

**Output Description**
- Always return a JSON object with exactly this schema:
  {json.dumps(cls.model_json_schema(), indent=4)}
"""
