# src/aloegraph/V2/agent/v2_chat_model.py
"""
v2_chat_agent_model
===================

- **Module:** `src/aloegraph/V2/agent/v2_chat_model.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

State object for managing chat sessions in AloeGraph V2.

This module defines `ChatAgentState`, which extends `V2AloeConfig` to
track the full lifecycle of a conversation. It integrates intake and
routing states with a chronological chat log, ensuring that all user
and agent messages are recorded with sequence IDs and timestamps.

Overview
--------
- **ChatAgentState**:
  * Maintains a `chat_log` of messages with sequence IDs and timestamps.
  * Holds nested `IntakeAgentState` and `RouterAgentState` objects for
    triage and routing decisions.
  * Provides helper methods to push user and agent messages into the log.

Integration
-----------
- Serves as the central state object for chat workflows in AloeGraph.
- Works in tandem with:
    * `IntakeAgent` — triages user messages at the start of a workflow.
    * `RouterAgent` — routes task‑oriented requests to downstream agents.
- Ensures reproducibility and transparency by logging every message.

Mermaid Diagram
---------------
```mermaid
flowchart TD
    U[User Message] --> I[IntakeAgentState]
    I --> R[RouterAgentState]
    R --> C[ChatAgentState.chat_log]
    C --> End[Conversation Record]
```
"""

import aloegraph.V2.v2_base_model as v2_base_model
import aloegraph.V2.agent.v2_intake_model as v2_intake_model
import aloegraph.V2.agent.v2_router_model as v2_router_model

import time


class ChatAgentState(v2_base_model.V2AloeConfig):
    """
    State object for the Chat Agent in AloeGraph V2.

    Extends `V2AloeConfig` to track the full lifecycle of a chat session,
    including intake decisions, routing state, and a chronological log of
    user and agent messages. This state object acts as the central record
    of conversation flow.

    Responsibilities
    ----------------
    - Maintain a `chat_log` of all messages exchanged between user and agent.
    - Increment and track a `chat_sequence_counter` for ordered message IDs.
    - Hold nested state objects for:
        * `intake_agent_state` — triage decisions at the start of a workflow.
        * `router_agent_state` — routing decisions and downstream agent state.
    - Provide helper methods to push user and agent messages into the log.

    Attributes
    ----------
    chat_log : list[ChatMessage]
        Chronological list of all messages in the conversation.
    chat_sequence_counter : int
        Counter used to assign sequential IDs to messages.
    intake_agent_state : IntakeAgentState
        Nested state object for the Intake Agent.
    router_agent_state : RouterAgentState
        Nested state object for the Router Agent.

    Methods
    -------
    push_user_message(state: V2AloeConfig) -> ChatMessage
        Append a user message from the given state to the chat log.
    push_agent_message(state: V2AloeConfig) -> ChatMessage
        Append an agent message from the given state to the chat log.
    push_message(role: str, msg: str, error: str) -> ChatMessage
        Append a message with the given role, content, and error to the log,
        incrementing the sequence counter and timestamping the entry.

    Example
    -------
    ``` python
    state = ChatAgentState()
    user_state = v2_base_model.V2AloeConfig(user_message="Hello!")
    state.push_user_message(user_state)
    
    > ChatMessage(sequence_id=1, role="User", content="Hello!", ...)
    ```

    ``` python
    agent_state = v2_base_model.V2AloeConfig(agent_message="Hi there!")
    state.push_agent_message(agent_state)

    > ChatMessage(sequence_id=2, role="Agent", content="Hi there!", ...)
    ```
    """

    chat_log: list[v2_base_model.ChatMessage] = []
    chat_sequence_counter: int = 0
    intake_agent_state: v2_intake_model.IntakeAgentState = v2_intake_model.IntakeAgentState()
    router_agent_state: v2_router_model.RouterAgentState = v2_router_model.RouterAgentState()

    def push_user_message(self, state: v2_base_model.V2AloeConfig) -> v2_base_model.ChatMessage:
        return self.push_message(role="User", msg=state.user_message, error=state.error_message)

    def push_agent_message(self, state: v2_base_model.V2AloeConfig) -> v2_base_model.ChatMessage:
        return self.push_message(role="Agent", msg=state.agent_message, error=state.error_message)

    def push_message(self, role, msg, error) -> v2_base_model.ChatMessage:
        self.chat_sequence_counter += 1
        chat_message = v2_base_model.ChatMessage(
            sequence_id=self.chat_sequence_counter,
            role=role,
            content=msg,
            error_message=error,
            timestamp=f"{time.strftime('%H:%M:%S')}"
        )
        self.chat_log.append(chat_message)
        return chat_message
