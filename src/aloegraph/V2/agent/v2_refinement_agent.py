# src/aloegraph/V2/agent/v2_refinement_agent.py
"""
v2_refinement_agent
===================

- **Module:** `src/aloegraph/V2/agent/v2_refinement_agent.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Graph implementation of the refinement agent in AloeGraph V2.

This module defines `RefinementAgent`, a specialized `V2AloeGraph` that
orchestrates iterative refinement workflows. It guides the user through
cycles of requesting refinements, applying them to items, committing
results, and handling interrupts or resumes. Each stage of the workflow
is represented as a graph node, with transitions defined by `@AloeNode`
and `@AloeEdge` decorators.

Overview
--------
- **RefinementAgent**:
  A graph that:
    * Starts in `check_auto_request` to decide whether refinements should
      be requested automatically.
    * Moves into `ready` state when awaiting user input.
    * Handles interrupts (`ready_interrupt`, `refining_interrupt`) and
      resumes (`ready_resume`, `refining_resume`) gracefully.
    * Requests refinements via `request_refinements` and processes them
      in `process_metarefinements`.
    * Decides whether refinements exist (`check_has_refinements`) and
      transitions into `refining` or back to `ready`.
    * Commits refinements (`commit`) and checks whether to auto‑continue
      (`check_auto_continue`).

Integration
-----------
The agent uses `JSONResponseGeneratorBase` instances to enforce structured
outputs for each refinement state:
- `RefinementAgentReadyInterruptResponse`
- `RefinementAgentReadyResumeResponse`
- `RefinementAgentRefiningInterruptResponse`
- `RefinementAgentRefiningResumeResponse`
- `RefinementAgentRequestRefinementsResponse`

Mermaid Diagram
---------------
```mermaid
flowchart TD
    Start[check_auto_request] --> Ready[ready]
    Start --> Request[request_refinements]

    Ready -->|Interrupt| RI[ready_interrupt]
    RI --> RR[ready_resume]
    RR --> Ready
    RR --> Request
    RR --> End[END]

    Request --> Process[process_metarefinements]
    Process --> Check[check_has_refinements]

    Check -->|Has refinements| Refining[refining]
    Check -->|No refinements| Ready

    Refining -->|Interrupt| FI[refining_interrupt]
    FI --> FR[refining_resume]
    FR --> Refining
    FR --> Commit[commit]
    FR --> Request

    Commit --> Auto[check_auto_continue]
    Auto -->|auto_continue=True| End
    Auto -->|auto_continue=False| Start
```    
"""

import aloegraph.V2.v2_base_model as v2_base_model
import aloegraph.V2.agent.v2_refinement_model as v2_refinement_model
import aloegraph.V2.agent.v2_refinement_response as v2_refinement_response
from aloegraph.V2.graph.v2_aloe_node import AloeNode, AloeEdge
from aloegraph.V2.v2_aloe_graph import V2AloeGraph
from aloegraph.V2.v2_base_model import END
from aloegraph.V2.response_generator import JSONResponseGeneratorBase

from pydantic import BaseModel, Field


class RefinementAgent(V2AloeGraph[v2_refinement_model.RefinementAgentState]):
    """
    Refinement agent graph for AloeGraph V2.

    `RefinementAgent` extends `V2AloeGraph` to implement iterative refinement
    workflows. It guides the user through cycles of requesting refinements,
    applying them to items, committing results, and handling interrupts or
    resumes. Each stage of the workflow is represented as a graph node, with
    transitions defined by `@AloeNode` and `@AloeEdge` decorators.

    Responsibilities
    ----------------
    - Manage refinement state (`RefinementAgentState`) including refinements,
      refinable items, and automation flags.
    - Define graph nodes for key refinement stages:
        * `check_auto_request` — entry point, decides whether to request refinements automatically.
        * `ready` — idle state awaiting user input.
        * `ready_interrupt` — handles interrupts in the ready state.
        * `ready_resume` — resumes from ready state, deciding whether to continue or request refinements.
        * `request_refinements` — requests refinements from the user via a response generator.
        * `process_metarefinements` — processes meta‑refinements before checking availability.
        * `check_has_refinements` — decision node to branch into refining or return to ready.
        * `refining` — active refinement state.
        * `refining_interrupt` — handles interrupts during refinement.
        * `refining_resume` — resumes refinement, deciding whether to continue, commit, or request more.
        * `commit` — commits refinements and transitions to auto‑continue check.
        * `check_auto_continue` — decides whether to continue automatically or return to request stage.
    - Integrate with response generators (`JSONResponseGeneratorBase`) to
      enforce structured outputs for each refinement state.
    - Handle interrupts (`__INTERRUPT__`) and resumes (`__RESUME__`) gracefully
      during refinement cycles.

    Attributes
    ----------
    state : RefinementAgentState
        The current refinement state, including refinements, items, and flags.
    ready_interrupt_response_generator : JSONResponseGeneratorBase[RefinementAgentReadyInterruptResponse]
        Generator for producing structured responses when interrupting in ready state.
    ready_resume_response_generator : JSONResponseGeneratorBase[RefinementAgentReadyResumeResponse]
        Generator for producing structured responses when resuming from ready state.
    refinement_interrupt_response_generator : JSONResponseGeneratorBase[RefinementAgentRefiningInterruptResponse]
        Generator for producing structured responses when interrupting during refinement.
    refinement_resume_response_generator : JSONResponseGeneratorBase[RefinementAgentRefiningResumeResponse]
        Generator for producing structured responses when resuming refinement.
    request_refinement_response_generator : JSONResponseGeneratorBase[RefinementAgentRequestRefinementsResponse]
        Generator for producing structured responses when requesting refinements.

    Example
    -------
    ```python
    from aloegraph.V2.agent.v2_refinement_model import RefinementAgentState
    from aloegraph.V2.agent.v2_refinement_response import (
        RefinementAgentReadyInterruptResponse,
        RefinementAgentReadyResumeResponse,
        RefinementAgentRefiningInterruptResponse,
        RefinementAgentRefiningResumeResponse,
        RefinementAgentRequestRefinementsResponse,
    )
    from aloegraph.V2.response_generator import GeminiJSONResponseGenerator

    # Initialize refinement agent
    initial_state = RefinementAgentState()
    agent = RefinementAgent(
        initial_state,
        ready_interrupt_response_generator=GeminiJSONResponseGenerator[RefinementAgentReadyInterruptResponse](client, "ReadyInterrupt", "Handle ready interrupts"),
        ready_resume_response_generator=GeminiJSONResponseGenerator[RefinementAgentReadyResumeResponse](client, "ReadyResume", "Resume from ready"),
        refinement_interrupt_response_generator=GeminiJSONResponseGenerator[RefinementAgentRefiningInterruptResponse](client, "RefiningInterrupt", "Handle refining interrupts"),
        refinement_resume_response_generator=GeminiJSONResponseGenerator[RefinementAgentRefiningResumeResponse](client, "RefiningResume", "Resume refining"),
        request_refinement_response_generator=GeminiJSONResponseGenerator[RefinementAgentRequestRefinementsResponse](client, "RequestRefinements", "Request refinements"),
    )

    # Compile and run the refinement workflow
    agent.compile()
    final_state = agent.invoke(initial_state)
    ```
    """

    @AloeNode(is_entry=True, node_render_shape=v2_base_model.NodeRenderShape.HEXAGON)
    @AloeEdge(target="request_refinements")
    @AloeEdge(target="ready")
    def check_auto_request(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        raise NotImplementedError()
        return state

    @AloeNode()
    @AloeEdge(target="ready_interrupt")
    def ready(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        raise NotImplementedError()
        return state

    @AloeNode(node_render_shape=v2_base_model.NodeRenderShape.TRAP_ALT)
    @AloeEdge(target="ready_resume", interrupt=True)
    def ready_interrupt(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        #
        # Call Model
        #
        raise NotImplementedError()
        response: v2_refinement_response.RefinementAgentReadyInterruptResponse =\
            self.ready_interrupt_response_generator.generate(XXXX)
        return state

    @AloeNode(node_render_shape=v2_base_model.NodeRenderShape.TRAP)
    @AloeEdge(target="ready")
    @AloeEdge(target="request_refinements")
    @AloeEdge(target=END)
    def ready_resume(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        #
        # Call Model
        #
        raise NotImplementedError()
        response = v2_refinement_response.RefinementAgentReadyResumeResponse(
            **self.ready_resume_response_generator.generate(state.user_message))
        # if response.requestRefinements
        # if response.shouldContinue
        # if state.hasRefinements:
        return state

    @AloeNode()
    @AloeEdge(target="process_metarefinements")
    def request_refinements(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        #
        # Call Model
        #
        raise NotImplementedError()
        response: v2_refinement_response.RefinementAgentRequestRefinementsResponse =\
            self.request_refinement_response_generator.generate(XXXX)
        return state

    @AloeNode()
    @AloeEdge(target="check_has_refinements")
    def process_metarefinements(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        raise NotImplementedError()
        state.__EDGE__ = "check_has_refinements"
        return state

    @AloeNode(node_render_shape=v2_base_model.NodeRenderShape.DIAMOND)
    @AloeEdge(target="ready")
    @AloeEdge(target="refining")
    def check_has_refinements(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        raise NotImplementedError()
        if state.hasRefinements():
            state.__EDGE__ = "refining"
        else:
            state.__EDGE__ = "ready"
        return state

    @AloeNode()
    @AloeEdge(target="refining_interrupt")
    def refining(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        raise NotImplementedError()
        return state

    @AloeNode(node_render_shape=v2_base_model.NodeRenderShape.TRAP_ALT)
    @AloeEdge(target="refining_resume", interrupt=True)
    def refining_interrupt(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        #
        # Call Model
        #
        raise NotImplementedError()
        response: v2_refinement_response.RefinementAgentRefiningInterruptResponse =\
            self.refinement_interrupt_response_generator.generate(XXXX)
        state.__EDGE__ = "refining_resume"
        return state

    @AloeNode(node_render_shape=v2_base_model.NodeRenderShape.TRAP)
    @AloeEdge(target="refining")
    @AloeEdge(target="commit")
    @AloeEdge(target="request_refinements")
    def refining_resume(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        #
        # Call Model
        #
        raise NotImplementedError()
        response: v2_refinement_response.RefinementAgentRefiningResumeResponse =\
            self.refinement_resume_response_generator.generate(
                state.user_message)
        return state

    @AloeNode()
    @AloeEdge(target="check_auto_continue")
    def commit(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        raise NotImplementedError()
        state.__EDGE__ = "check_auto_continue"
        return state

    @AloeNode(node_render_shape=v2_base_model.NodeRenderShape.HEXAGON)
    @AloeEdge(target="check_auto_request")
    @AloeEdge(target=END)
    def check_auto_continue(self, state: v2_refinement_model.RefinementAgentState) -> v2_refinement_model.RefinementAgentState:
        raise NotImplementedError()
        if state.auto_continue:
            state.__EDGE__ = END
        else:
            state.__EDGE__ = "check_auto_request"
        return state

    def __init__(self,
                 initial_state: v2_refinement_model.RefinementAgentState,
                 ready_interrupt_response_generator: JSONResponseGeneratorBase[v2_refinement_response.RefinementAgentReadyInterruptResponse],
                 ready_resume_response_generator: JSONResponseGeneratorBase[v2_refinement_response.RefinementAgentReadyResumeResponse],
                 refinement_interrupt_response_generator: JSONResponseGeneratorBase[v2_refinement_response.RefinementAgentRefiningInterruptResponse],
                 refinement_resume_response_generator: JSONResponseGeneratorBase[v2_refinement_response.RefinementAgentRefiningResumeResponse],
                 request_refinement_response_generator: JSONResponseGeneratorBase[
                     v2_refinement_response.RefinementAgentRequestRefinementsResponse]
                 ):
        self.state = initial_state
        self.ready_interrupt_response_generator: JSONResponseGeneratorBase[
            v2_refinement_response.RefinementAgentReadyInterruptResponse] = ready_interrupt_response_generator
        self.ready_resume_response_generator: JSONResponseGeneratorBase[
            v2_refinement_response.RefinementAgentReadyResumeResponse] = ready_resume_response_generator
        self.refinement_interrupt_response_generator: JSONResponseGeneratorBase[
            v2_refinement_response.RefinementAgentRefiningInterruptResponse] = refinement_interrupt_response_generator
        self.refinement_resume_response_generator: JSONResponseGeneratorBase[
            v2_refinement_response.RefinementAgentRefiningResumeResponse] = refinement_resume_response_generator
        self.request_refinement_response_generator: JSONResponseGeneratorBase[
            v2_refinement_response.RefinementAgentRequestRefinementsResponse] = request_refinement_response_generator
