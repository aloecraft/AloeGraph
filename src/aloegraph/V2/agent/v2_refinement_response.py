# src/aloegraph/V2/agent/v2_refinement_response.py
"""
v2_refinement_response
=======================

- **Module:** `src/aloegraph/V2/agent/v2_refinement_response.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Response schemas for refinement agents in AloeGraph V2.

This module defines a set of `BaseResponse` subclasses that capture the
different states and transitions of a refinement agent. Refinement agents
guide users through iterative improvement of artifacts, handling interrupts,
resumes, and requests for refinements in a structured way.

Overview
--------
- **RefinementAgentReadyInterruptResponse**:
  Used when the agent is in a "ready" state but must pause or stop, while
  still providing a message to the user.

- **RefinementAgentReadyResumeResponse**:
  Used when resuming from a "ready" state. Indicates whether the agent
  should request refinements or continue directly.

- **RefinementAgentRefiningInterruptResponse**:
  Used when the agent is actively refining but must pause or stop, while
  still providing a message to the user.

- **RefinementAgentRefiningResumeResponse**:
  Used when resuming from an active refining state. Indicates whether the
  agent should request refinements, commit them, or auto‑continue.

- **RefinementAgentRequestRefinementsResponse**:
  Used when the agent explicitly requests refinements from the user,
  providing a list of `V2Refinement` options.

Responsibilities
----------------
- Provide structured, validated outputs for each refinement state.
- Enforce predictable transitions between ready, refining, interrupt,
  resume, and request states.
- Supply system instructions that ensure agents return JSON conforming
  to the expected schema.

Mermaid Diagram
---------------
```mermaid
flowchart TD
    Ready[Ready State] -->|Interrupt| RI[ReadyInterruptResponse]
    Ready -->|Resume| RR[ReadyResumeResponse]

    Refining[Refining State] -->|Interrupt| FI[RefiningInterruptResponse]
    Refining -->|Resume| FR[RefiningResumeResponse]
    Refining -->|Request| RQ[RequestRefinementsResponse]

    RQ --> Refining
    RI --> End[END]
    FI --> End
    RR --> Refining
    FR --> Commit[Commit Refinements]
```    
"""

from aloegraph.V2.agent.v2_refinement_model import V2Refinement
from aloegraph.V2.v2_base_response import BaseResponse

import json

class RefinementAgentReadyInterruptResponse(BaseResponse):
    """
    Response schema for interrupting the refinement agent when it is in a
    "ready" state.

    Used when the agent needs to pause or stop before beginning refinement,
    while still providing a message back to the user.

    Attributes
    ----------
    agent_message : str
        The message produced by the agent to explain or acknowledge the
        interrupt event.

    Class Methods
    -------------
    SYSTEM_INSTRUCTION(agent_name, agent_description) -> str
        Returns the system prompt instructing the agent to output JSON
        conforming to this schema.
    """
    agent_message: str

    @classmethod
    def SYSTEM_INSTRUCTION(cls, agent_name: str, agent_description: str):
        return f"""
**Output Description**
- Always return a JSON object with exactly this schema:
  {json.dumps(cls.model_json_schema(), indent=4)}
"""


class RefinementAgentReadyResumeResponse(BaseResponse):
    """
    Response schema for resuming the refinement agent from a "ready" state.

    Used when the agent is asked to continue or request refinements before
    moving forward.

    Attributes
    ----------
    request_refinements : bool
        True if the agent should request refinements from the user.
    should_continue : bool
        True if the agent should continue without requesting refinements.

    Class Methods
    -------------
    SYSTEM_INSTRUCTION(agent_name, agent_description) -> str
        Returns the system prompt instructing the agent to output JSON
        conforming to this schema.
    """

    request_refinements: bool
    should_continue: bool

    @classmethod
    def SYSTEM_INSTRUCTION(cls, agent_name: str, agent_description: str):
        return f"""
**Output Description**
- Always return a JSON object with exactly this schema:
  {json.dumps(cls.model_json_schema(), indent=4)}
"""


class RefinementAgentRefiningInterruptResponse(BaseResponse):
    """
    Response schema for interrupting the refinement agent while it is
    actively refining.

    Used when the agent needs to pause or stop during refinement, while
    still providing a message back to the user.

    Attributes
    ----------
    agent_message : str
        The message produced by the agent to explain or acknowledge the
        interrupt event.

    Class Methods
    -------------
    SYSTEM_INSTRUCTION(agent_name, agent_description) -> str
        Returns the system prompt instructing the agent to output JSON
        conforming to this schema.
    """
    agent_message: str

    @classmethod
    def SYSTEM_INSTRUCTION(cls, agent_name: str, agent_description: str):
        return f"""
**Output Description**
- Always return a JSON object with exactly this schema:
  {json.dumps(cls.model_json_schema(), indent=4)}
"""


class RefinementAgentRefiningResumeResponse(BaseResponse):
    """
    Response schema for resuming the refinement agent while it is actively
    refining.

    Used when the agent is asked to continue, commit refinements, or
    auto‑continue without further user input.

    Attributes
    ----------
    request_refinements : bool
        True if the agent should request additional refinements.
    should_commit : bool
        True if the agent should commit the current refinements.
    should_auto_continue : bool
        True if the agent should continue automatically without further
        user input.

    Class Methods
    -------------
    SYSTEM_INSTRUCTION(agent_name, agent_description) -> str
        Returns the system prompt instructing the agent to output JSON
        conforming to this schema.
    """

    request_refinements: bool
    should_commit: bool
    should_auto_continue: bool

    @classmethod
    def SYSTEM_INSTRUCTION(cls, agent_name: str, agent_description: str):
        return f"""
**Output Description**
- Always return a JSON object with exactly this schema:
  {json.dumps(cls.model_json_schema(), indent=4)}
"""


class RefinementAgentRequestRefinementsResponse(BaseResponse):
    """
    Response schema for requesting refinements from the user.

    Used when the agent needs to present a list of possible refinements
    and ask the user to select or provide feedback.

    Attributes
    ----------
    refinements : list[V2Refinement]
        A list of refinement options proposed by the agent.

    Class Methods
    -------------
    SYSTEM_INSTRUCTION(agent_name, agent_description) -> str
        Returns the system prompt instructing the agent to output JSON
        conforming to this schema.
    """
    refinements: list[V2Refinement]

    @classmethod
    def SYSTEM_INSTRUCTION(cls, agent_name: str, agent_description: str):
        return f"""
**Output Description**
- Always return a JSON object with exactly this schema:
  {json.dumps(cls.model_json_schema(), indent=4)}
"""
