from typing import Any, Dict, Type, Union, List, Optional
from pydantic import BaseModel, Field

from google import genai

from aloegraph.gemini.util import generate_json_response
from aloegraph.interface.chat_agent import ChatAgent
from aloegraph.interface.chat_dialog import ChatDialog

class GeminiChatAgentResponse(BaseModel):
  agent_message: str

class GeminiChatAgent(ChatAgent):

  def __init__(self, client: genai.Client):
    self.client = client
    self.dialog = None
    self.system_instruction = "You are a helpful assistant"

  def notify(self, msg:str) -> str:
      response: Dict[str, Any] = generate_json_response(
        self.client, 
        prompt= msg,
        system_instruction=self.system_instruction,
        output_schema = GeminiChatAgentResponse,
        model_type="gemini-2.5-flash"
      )

      gemini_reply = GeminiChatAgentResponse(**response)

      if self.dialog:
        self.dialog.add_reply(f"{gemini_reply.agent_message}", "agent")

  def set_dialog(self, dialog: ChatDialog) -> None:
    self.dialog = dialog

  @classmethod
  def factory(cls, client: genai.Client, dialog: ChatDialog)->"GeminiChatAgent":
    """
    Usage Example:
    ---
    from aloegraph.agent.simple_gemini_chat_agent import GeminiChatAgentResponse, GeminiChatAgent
    from aloegraph.dialog.notebook_chat_dialog import NotebookChatDialog

    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    notebook_dialog = NotebookChatDialog()
    agent = GeminiChatAgent.factory(client, notebook_dialog)
    """
    agent = cls(client)
    dialog.set_agent(agent)
    agent.set_dialog(dialog)
    return agent