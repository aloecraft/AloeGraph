from .model.base_model import AloeChatMessage, AloeChat, AloeEdge

from pydantic import BaseModel, Field
from typing import Callable, Optional, Union, Literal

class AloeConfig(BaseModel):
  current_node: str
  desired_node: Optional[str] = None
  nodes: dict[str, Callable] = Field(default_factory=dict, exclude=True)
  edges: dict[str, AloeEdge] = Field(default_factory=dict)
  chat: AloeChat = Field(default_factory=lambda: AloeChat(messages=[]))
  agent_message: Optional[str] = ""
  error_message: Optional[str] = ""

  def get_available_transitions(self) -> list[str]:
    current = self.current_node
    if current not in self.edges:
        return []

    available = []
    for t in self.edges[current].targets:
        edge = self.edges.get(t)
        if not edge:
            # If we don’t have an AloeEdge for this target, skip it
            continue
        if all(check(self) for check in edge.transition_checks):
            available.append(t)
    return available

  def to_string(self, indent="\t") -> str:
        return  \
          f"\n{indent}current_node: {self.current_node}" + \
          f"\n{indent}Chat:" + \
          f"\n{self.chat.to_string(indent+'\t')}"