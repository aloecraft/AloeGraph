from abc import ABC, abstractmethod

class ChatDialog(ABC):

  @abstractmethod
  def set_agent(self, agent: "ChatAgent") -> None:
    pass

  @abstractmethod
  def add_reply(self, text: str, sender: str = None) -> None:
    pass

  @abstractmethod
  def add_log(self, text: str) -> None:
    pass

  @abstractmethod
  def clear_log(self) -> None:
    pass

  @abstractmethod
  def clear_msgs(self) -> None:
    pass

  @abstractmethod
  def set_status(self, text: str) -> None:
    pass