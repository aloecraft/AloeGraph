# src/aloegraph/V2/agent/v2_chat_agent.py
"""
v2_chat_agent
=============

- **Module:** `src/aloegraph/V2/agent/v2_chat_agent.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Graph implementation of the Chat Agent in AloeGraph V2.

This module defines `ChatAgent`, the orchestrator of full chat workflows.
It integrates the Intake Agent (triage) and Router Agent (task routing),
manages conversation state, and ensures that user and agent messages are
logged and delivered consistently.

Overview
--------
- **ChatAgent**:
  * Entry point for chat workflows (`invoke_intake`).
  * Decides whether to respond directly or route requests downstream.
  * Invokes Router Agent when routing is required.
  * Pushes agent messages to the chat log and notifies replies.
  * Supports auto‑resume for multi‑turn routing workflows.

Integration
-----------
- Works in tandem with:
    * `ChatAgentState` — holds intake, routing, and chat log state.
    * `IntakeAgent` — triages user messages.
    * `RouterAgent` — routes task‑oriented requests.
    * `ChatNotifier` — delivers agent replies externally.
- Serves as the top‑level agent graph coordinating intake and routing.

Mermaid Diagram
---------------
```mermaid
flowchart TD
    U[User Message] --> I[invoke_intake]
    I -->|should_route=True| R[invoke_route]
    I -->|should_route=False| CM[chat_message]
    R --> CM
    CM --> AR[auto_resume]
    AR -->|resume=True| R
    AR -->|resume=False| End[END]
```
"""

from aloegraph.V2.graph.v2_aloe_node import AloeNode, AloeEdge
from aloegraph.V2.v2_aloe_graph import V2AloeGraph
from aloegraph.V2.v2_base_model import END
import aloegraph.V2.v2_base_model as v2_base_model

import aloegraph.V2.agent.v2_intake_agent as v2_intake_agent
import aloegraph.V2.agent.v2_router_agent as v2_router_agent
import aloegraph.V2.agent.v2_chat_model as v2_chat_model


class ChatAgent(V2AloeGraph[v2_chat_model.ChatAgentState], v2_base_model.ChatAgent):
    """
    Chat agent graph for AloeGraph V2.

    `ChatAgent` extends `V2AloeGraph` and `ChatAgent` base functionality to
    orchestrate full chat workflows. It integrates the Intake Agent and
    Router Agent, manages conversation state, and ensures that user and
    agent messages are logged and delivered consistently.

    Responsibilities
    ----------------
    - Define graph nodes for the chat workflow:
        * `invoke_intake` — entry node; pushes user message, invokes Intake Agent,
          and decides whether to route or reply directly.
        * `invoke_route` — invokes the Router Agent when routing is required.
        * `chat_message` — pushes agent message to the chat log and notifies reply.
        * `auto_resume` — decides whether to resume routing or end the workflow.
    - Manage conversation state (`ChatAgentState`) including intake and routing
      sub‑states.
    - Integrate with `ChatNotifier` to deliver agent replies externally.
    - Validate dependencies and compile sub‑agents via `preflight`.

    Attributes
    ----------
    state : ChatAgentState
        Current chat state, including intake, routing, and chat log.
    intake_agent : IntakeAgent
        Sub‑agent responsible for triage decisions.
    router_agent : RouterAgent
        Sub‑agent responsible for routing task‑oriented requests.
    reply_notifier : ChatNotifier
        Notifier used to deliver agent replies to external systems.

    Methods
    -------
    invoke_intake(state) -> ChatAgentState
        Entry node; processes user message, invokes Intake Agent, and sets edge.
    invoke_route(state) -> ChatAgentState
        Invokes Router Agent and updates agent message.
    chat_message(state) -> ChatAgentState
        Pushes agent message to chat log and notifies reply.
    auto_resume(state) -> ChatAgentState
        Decides whether to resume routing or end workflow.
    preflight() -> bool
        Validates dependencies and compiles sub‑agents if needed.
    compile(reply_notifier, graph_name) -> None
        Compiles the chat agent graph with notifier and name.
    notify(msg) -> str
        Sends a user message into the workflow and invokes the graph.
    set_dialog(dialog) -> None
        Not implemented; use `ChatNotifier` instead.

    Example
    -------
    ```python
    from aloegraph.V2.agent.v2_chat_model import ChatAgentState
    from aloegraph.V2.agent.v2_intake_agent import IntakeAgent
    from aloegraph.V2.agent.v2_router_agent import RouterAgent
    from aloegraph.V2.v2_base_model import ChatNotifier

    initial_state = ChatAgentState()
    intake = IntakeAgent(initial_state.intake_agent_state, response_generator)
    router = RouterAgent(initial_state.router_agent_state, response_generator)
    notifier = ChatNotifier()

    agent = ChatAgent(initial_state, intake, router, notifier)
    agent.compile(reply_notifier=notifier, graph_name="chat_agent")

    agent.notify("Hello, what can you do?")
    ```
    """

    @AloeNode(is_entry=True, node_render_shape=v2_base_model.NodeRenderShape.CIRCLE)
    @AloeEdge(target="invoke_route")
    @AloeEdge(target="chat_message")
    def invoke_intake(self, state: v2_chat_model.ChatAgentState) -> v2_chat_model.ChatAgentState:
        state.push_user_message(state=state)

        self.notify_log("----------------")
        self.notify_log("--------")

        state.intake_agent_state.user_message = state.user_message
        state.intake_agent_state = \
            self.intake_agent.invoke(state.intake_agent_state)
        if state.intake_agent_state.should_route:
            state.__EDGE__ = "invoke_route"
        else:
            state.agent_message = state.intake_agent_state.agent_message
            state.__EDGE__ = "chat_message"
        return state

    @AloeNode(node_render_shape=v2_base_model.NodeRenderShape.CIRCLE)
    @AloeEdge(target="chat_message")
    def invoke_route(self, state: v2_chat_model.ChatAgentState) -> v2_chat_model.ChatAgentState:
        state.router_agent_state.parent_state = state
        state.router_agent_state.user_message = state.user_message
        state.router_agent_state = \
            self.router_agent.invoke(state.router_agent_state)
        state.agent_message = state.router_agent_state.agent_message
        state.__EDGE__ = "chat_message"
        return state

    @AloeNode(node_render_shape=v2_base_model.NodeRenderShape.ASYM)
    @AloeEdge(target="auto_resume")
    def chat_message(self, state: v2_chat_model.ChatAgentState) -> v2_chat_model.ChatAgentState:
        agent_message = state.push_agent_message(state=state)
        self.reply_notifier.add_reply(
            agent_message.content, agent_message.role)
        state.__EDGE__ = "auto_resume"
        return state

    @AloeNode(node_render_shape=v2_base_model.NodeRenderShape.HEXAGON)
    @AloeEdge(target="invoke_route")
    @AloeEdge(target=END)
    def auto_resume(self, state: v2_chat_model.ChatAgentState) -> v2_chat_model.ChatAgentState:
        if state.router_agent_state.__RESUME__:
            state.__EDGE__ = "invoke_route"
        else:
            state.__EDGE__ = END
        return state

    def preflight(self) -> bool:
        from aloegraph.V2.exception.base_exceptions import AloeGraphCompileError
        if not isinstance(self.reply_notifier, v2_base_model.ChatNotifier):
            raise AloeGraphCompileError(
                "ChatAgent.reply_notifier Not Set(v2_base_model.ChatNotifier)")
        if not isinstance(self.intake_agent, v2_intake_agent.IntakeAgent):
            raise AloeGraphCompileError(
                "ChatAgent.intake_agent Not Set (v2_intake_agent.IntakeAgent)")
        if not isinstance(self.router_agent, v2_router_agent.RouterAgent):
            raise AloeGraphCompileError(
                "ChatAgent.router_agent Not Set (v2_router_agent.RouterAgent)")
        if not self.intake_agent._is_initialized:
            self.intake_agent.compile(
                "intake_agent", log_notifier=self.reply_notifier)
        if not self.router_agent._is_initialized:
            self.router_agent.compile(
                "router_agent", log_notifier=self.reply_notifier)
        return super().preflight()

    def compile(self, reply_notifier: v2_base_model.ChatNotifier, graph_name: str) -> None:
        if reply_notifier:
            self.reply_notifier = reply_notifier
        super().compile(graph_name=graph_name, log_notifier=self.reply_notifier)

    def notify(self, msg: str) -> str:
        self.state.user_message = msg
        self.invoke()

    def set_dialog(self, dialog: "ChatDialog") -> None:
        raise NotImplementedError("Should use ChatNotifier")

    def __init__(self,
                 initial_state: v2_chat_model.ChatAgentState,
                 intake_agent: v2_intake_agent.IntakeAgent,
                 router_agent: v2_router_agent.RouterAgent,
                 reply_notifier: v2_base_model.ChatNotifier = None):
        self.state = initial_state
        self.intake_agent = intake_agent
        self.router_agent = router_agent
        self.reply_notifier = reply_notifier
