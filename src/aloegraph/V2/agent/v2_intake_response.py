# src/aloegraph/V2/agent/v2_intake_response.py
"""
v2_intake_response
========================

- **Module:** `src/aloegraph/V2/agent/v2_intake_response.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Response schema for the Intake Agent in AloeGraph V2.

This module defines `IntakeAgentResponse`, the structured output used by
the Intake Agent to triage user messages. The Intake Agent sits at the
front of the AloeGraph workflow, deciding whether to respond directly
to system‑level questions or forward the request to the Router Agent for
task execution.

Overview
--------
- **IntakeAgentResponse**:
  Extends `BaseResponse` with fields for:
    * `should_route` — flag indicating whether the message should be
      handed off to the Router Agent.
    * `agent_message` — direct reply to the user if routing is not
      required.

Integration
-----------
The Intake Agent is the first stage in the AloeGraph pipeline:
- If the user asks about the system itself (e.g., what the agent is,
  how it works, onboarding questions), the Intake Agent responds
  directly.
- If the user’s request involves tasks, content generation, or
  application‑specific routes, the Intake Agent sets `should_route=True`
  and forwards the message to the Router Agent.

Mermaid Diagram
---------------
```mermaid
flowchart TD
    U[User Message] --> I[IntakeAgent]
    I -->|should_route=True| R[RouterAgent]
    I -->|should_route=False| M[Direct Agent Reply]
    R --> Downstream[Route Nodes / Tasks]
    M --> End[END]
```    
"""

import json
from pydantic import Field
from aloegraph.V2.v2_base_response import BaseResponse


class IntakeAgentResponse(BaseResponse):
    """
    Response schema for the Intake Agent in AloeGraph V2.

    The Intake Agent is responsible for triaging user messages: deciding
    whether to respond directly or forward the request to the Router Agent.
    This schema captures that decision and provides either a direct message
    or a routing flag.

    Attributes
    ----------
    should_route : bool, default False
        True if the user message should be routed to the Router Agent.
        False if the Intake Agent should respond directly.
    agent_message : str, optional
        Direct response to the user if `should_route` is False. Ignored
        when `should_route` is True.

    Class Methods
    -------------
    SYSTEM_INSTRUCTION(agent_name, agent_description) -> str
        Construct the system prompt for the Intake Agent. This prompt
        guides the agent to decide whether to respond directly or hand
        off to the Router Agent, and includes the JSON schema for
        validation.

    Example
    -------
    ``` python
     response = IntakeAgentResponse(
         should_route=False,
         agent_message="I am the Intake Agent. My role is triage."
     )
     print(response.should_route)   # False
     print(response.agent_message)  # "I am the Intake Agent. My role is triage."
    ```
    """

    should_route: bool = Field(
        default=False, description="True if user message should be routed, else false")
    agent_message: str = Field(
        default=None, description="Direct response to user if user message will not be routed by setting \"should_route\" to False. This value will be ignored if \"should_route\" is True")

    @classmethod
    def SYSTEM_INSTRUCTION(cls, agent_name: str, agent_description: str):
        return f"""
You are the Intake Agent for {agent_name}.

**What is {agent_name}?**

> {agent_description}

**Your role is triage:**
- Read the user’s latest message.
- Decide whether to respond directly or hand off to the Router Agent.

**Respond directly if:**
- The user asks about {agent_name} itself (what it is, how it works, it's capability).
- The user asks meta-questions about the chat system, onboarding, or your role.

**Hand off to the Router Agent if:**
- The user’s request involves performing tasks, generating content, or using application-specific Route Nodes.
- The request requires knowledge of prior conversation state beyond the last few turns.

**Guidelines:**
- Keep answers concise and explanatory when responding directly.
- Always preserve the user’s intent: either answer their system-level question or forward their request to the Router.

**Output Description**
- Always return a JSON object with exactly this schema:
  {json.dumps(cls.model_json_schema(), indent=4)}
"""
