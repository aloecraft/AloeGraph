from abc import ABC, abstractmethod
from .chat_dialog import ChatDialog

class ChatAgent(ABC):

  @abstractmethod
  async def notify(self, msg:str) -> str:
    pass

  @abstractmethod
  def set_dialog(self, dialog: ChatDialog) -> None:
    pass