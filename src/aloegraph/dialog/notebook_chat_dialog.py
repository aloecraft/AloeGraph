# src/aloegraph/dialog/notebook_chat_dialog.py
"""
notebook_chat_dialog
====================

- **Module:** `src/aloegraph/dialog/notebook_chat_dialog.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Interactive chat dialog integration for Jupyter notebooks in AloeGraph.

This module defines `NotebookChatDialog`, a concrete implementation of
`ChatNotifier` that uses `ipywidgets` to provide a simple user interface
for conversational agents inside a notebook environment. It enables
users to send messages to a `ChatAgent`, display replies, track logs,
and update status indicators directly within the notebook.

Overview
--------
- **dialog_factory**:
  Utility function that creates a styled, read‑only `Textarea` widget
  for displaying chat output or logs.

- **NotebookChatDialog**:
  Provides a notebook‑friendly chat interface with:
    * A text area for chat history
    * An input box and send button for user messages
    * A status output widget
    * A log output area for timestamped events

Responsibilities
----------------
- Manage user input and submission callbacks.
- Forward messages to an attached `ChatAgent` via `notify`.
- Display agent replies and status updates in the notebook UI.
- Record and clear logs for debugging or monitoring.
- Show/hide the chat interface dynamically.

Usage
-----
Instantiate `NotebookChatDialog` in a Jupyter notebook and attach a
`ChatAgent` to enable interactive conversations:

```python
from aloegraph.dialog.notebook_chat_dialog import NotebookChatDialog
from aloegraph.V2.v2_base_model import ChatAgent

dialog = NotebookChatDialog()
dialog.set_agent(my_agent)   # attach your ChatAgent
dialog.display()             # render the UI in the notebook
```
"""

import aloegraph.V2.v2_base_model as v2_base_model
import time

import ipywidgets as widgets
from IPython.display import display


def dialog_factory():
    """
    Create a styled, read-only text area widget for displaying chat output or logs.

    Returns
    -------
    ipywidgets.Textarea
        A Textarea widget configured with fixed width/height, wrapping, and disabled editing.
    """
    return widgets.Textarea(
        value="",
        layout={
            'width': '100%',
            'height': '350px',
        },
        style={
            'description_width': 'initial',
            'white-space': 'pre-wrap',   # preserve newlines, allow wrapping
            'overflow-wrap': 'break-word',  # break long words if needed
            'color': 'black'
        },
        disabled=True
    )


class NotebookChatDialog(v2_base_model.ChatNotifier):
    """
    Interactive chat dialog for Jupyter notebooks.

    This class provides a simple UI for sending messages to a ChatAgent and
    displaying responses, status updates, and logs. It uses ipywidgets to
    render a text area for chat history, an input box with a send button,
    and a log output area.

    Parameters
    ----------
    agent : v2_base_model.ChatAgent, optional
        The chat agent to notify when user input is submitted.
    """

    def set_agent(self, agent: v2_base_model.ChatAgent) -> v2_base_model.ChatAgent:
        """
        Attach a chat agent to this dialog.

        Parameters
        ----------
        agent : ChatAgent
            The agent to notify when user input is submitted.

        Returns
        -------
        ChatAgent
            The agent that was set.
        """
        self.agent = agent
        if not agent:
            self.set_indeterminant("no agent")
        else:
            self.set_active()
        return self.agent

    def __handle_submit(self, sender):
        """
        Internal callback for handling user input submission.

        Parameters
        ----------
        sender : Any
            The widget or event that triggered the submission.
        """
        input_val = self.pop_input()
        formatted_text = f"You: {input_val}\n"
        self.chat_output.value += formatted_text

        if self.agent:
            self.set_indeterminant()
            self.agent.notify(input_val)
            self.set_active()

    def pop_input(self) -> str:
        """
        Retrieve and clear the current text from the input box.

        Returns
        -------
        str
            The text entered by the user.
        """
        input_val = self.input_box.value
        self.input_box.value = ""
        return input_val

    def set_indeterminant(self, status: str = "..."):
        """
        Disable input controls and set status to indeterminant.

        Parameters
        ----------
        status : str, optional
            Status message to display, by default "..."
        """
        self.input_box.disabled = True
        self.input_btn.disabled = True
        self.set_status(status)

    def set_active(self, status: str = "ready."):
        """
        Enable input controls and set status to active.

        Parameters
        ----------
        status : str, optional
            Status message to display, by default "ready."
        """
        self.input_box.disabled = False
        self.input_btn.disabled = False
        self.set_status(status)

    def show(self):
        """Make the chat UI visible in the notebook."""
        self.chat_output.layout.display = ""
        self.status.layout.display = ""
        self.input_box.layout.display = ""

    def hide(self):
        """Hide the chat UI from the notebook display."""
        self.chat_output.layout.display = "none"
        self.status.layout.display = "none"
        self.input_box.layout.display = "none"

    def clear_input(self):
        """Hide the chat UI from the notebook display."""
        self.input_box.value = ""

    def set_status(self, text: str):
        """
        Update the status output widget.

        Parameters
        ----------
        text : str
            Status message to display.
        """
        self.status.outputs = ({
            'output_type': 'display_data',
            'data': {'text/plain': f"{text if text else ' '}"}
        },)

    def add_reply(self, text: str, sender: str = None):
        """
        Append a reply message to the chat output.

        Parameters
        ----------
        text : str
            The reply text.
        sender : str, optional
            Label for the sender, e.g. "Agent".
        """
        formatted_text = f"{sender + ': ' if sender else ''}{text}\n"
        self.chat_output.value += formatted_text

    def add_log(self, text: str):
        """
        Append a log entry with a timestamp.

        Parameters
        ----------
        text : str
            The log message.
        """
        formatted_text = f"{time.strftime('%H:%M:%S')} - {text}\n"
        self.log_output.value += formatted_text

    def clear_log(self) -> None:
        """Clear all log entries."""
        self.log_output.value = ""

    def clear_msgs(self) -> None:
        """Clear all chat messages."""
        self.chat_output.value = ""

    def __init_ui__(self):
        """Initialize the ipywidgets UI components."""
        self.chat_output = dialog_factory()
        self.status = widgets.Output()
        self.input_box = widgets.Text(
            placeholder="Type your message...", disabled=True)
        self.input_btn = widgets.Button(
            description="Send", button_style="info")
        self.log_output = dialog_factory()

        self.chat_input_ui = widgets.HBox([self.input_box, self.input_btn])
        self.chat_ui = widgets.VBox(
            [self.chat_output, self.status, self.chat_input_ui, self.log_output])

    def __init_listeners__(self):
        """Attach event listeners to input widgets."""
        self.input_box.on_submit(self.__handle_submit)
        self.input_btn.on_click(self.__handle_submit)

    def __init__(self):
        """Construct the NotebookChatDialog and initialize UI and listeners."""
        self.__init_ui__()
        self.__init_listeners__()
        self.set_agent(None)

    def display(self, init_msg: str = None):
        """
        Render the chat UI in the notebook.

        Parameters
        ----------
        init_msg : str, optional
            If provided, pre-fill the input box and submit it.
        """
        if init_msg:
            self.input_box.value = init_msg
            self.__handle_submit({})
        display(self.chat_ui)
