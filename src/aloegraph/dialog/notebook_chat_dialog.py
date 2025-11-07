from aloegraph.interface.chat_dialog import ChatDialog
from aloegraph.interface.chat_agent import ChatAgent

import ipywidgets as widgets

def dialog_factory():
  return widgets.Output(layout={
    'border': '1px solid gray',
    'height': '450px',
    'overflow_y': 'scroll',
    'resize':'vertical',
  })

from IPython.display import display
import time

class NotebookChatDialog(ChatDialog):

    def set_agent(self, agent: ChatAgent):
      self.agent = agent
      if not agent:
        self.set_indeterminant("no agent")
      else:
        self.set_active()

    def __handle_submit(self, sender):
      input_val = self.pop_input()
      formatted_text = f"You: {input_val}\n"
      self.chat_output.append_stdout(formatted_text)

      if self.agent:
        self.set_indeterminant()
        self.agent.notify(input_val)
        self.set_active()

    def pop_input(self)-> str:
        input_val = self.input_box.value
        self.input_box.value = ""
        return input_val

    def set_indeterminant(self, status: str = "..."):
        self.input_box.disabled = True
        self.input_btn.disabled = True
        self.set_status(status)

    def set_active(self, status: str = "ready."):
        self.input_box.disabled = False
        self.input_btn.disabled = False
        self.set_status(status)

    def show(self):
        self.chat_output.layout.display = ""
        self.status.layout.display = ""
        self.input_box.layout.display = ""

    def hide(self):
        self.chat_output.layout.display = "none"
        self.status.layout.display = "none"
        self.input_box.layout.display = "none"

    def clear_input(self):
        self.input_box.value = ""

    def set_status(self, text: str):
        self.status.outputs = ({
            'output_type': 'display_data',
            'data': {'text/plain': f"{text if text else ' ' }"}
        },)

    def add_reply(self, text: str, sender: str = None):
        formatted_text = f"{sender + ': ' if sender else ''}{text}\n"
        self.chat_output.append_stdout(formatted_text)

    def add_log(self, text: str):
        formatted_text = f"{time.strftime('%H:%M:%S')} - {text}\n"
        self.log_output.append_stdout(formatted_text)

    def clear_log(self) -> None:
        self.log_output.clear_output()
        self.log_output.outputs = ({
            'output_type': 'display_data',
            'data': {'text/plain': f""}
        },)

    def clear_msgs(self) -> None:
        self.chat_output.clear_output()
        self.chat_output.outputs = ({
            'output_type': 'display_data',
            'data': {'text/plain': f""}
        },)

    def __init_ui__(self):
        self.chat_output = dialog_factory()
        self.status = widgets.Output()
        self.input_box = widgets.Text(placeholder="Type your message...", disabled=True)
        self.input_btn = widgets.Button(description="Send", button_style="info")
        self.log_output = dialog_factory()

        self.chat_input_ui = widgets.HBox([self.input_box, self.input_btn])
        self.chat_ui = widgets.VBox([self.chat_output, self.status, self.chat_input_ui, self.log_output])

    def __init_listeners__(self):
        self.input_box.on_submit(self.__handle_submit)
        self.input_btn.on_click(self.__handle_submit)

    def __init__(self):
        self.__init_ui__()
        self.__init_listeners__()
        self.set_agent(None)

        display(self.chat_ui)