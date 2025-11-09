from pydantic import BaseModel, Field
from typing import Callable, Optional, Union, Literal

class AloeChatMessage(BaseModel):
  role: str
  content: str
  timestamp: str
  error_message: Optional[str] = None
  success: Optional[bool] = True

  def to_string(self, indent="\t"):
    return f"{indent}{ "🟢" if self.success else "⚠️"} {self.timestamp} - {self.role}: {self.content} {self.error_message or ''}"

class AloeChat(BaseModel):
  messages: list[AloeChatMessage]
  def to_string(self, indent="\t"):
    if not self.messages:
      return f"{indent}No messages\n"
    return f"{indent}Messages:\n" + f"\n{indent}".join([m.to_string(indent+"\t") for m in self.messages])

class AloeEdge(BaseModel):
    source: str
    targets: list[str]
    description: Optional[str] = None
    recommended_next: Optional[str] = None
    confirm_request: Optional[str] = None
    branch_decider: Callable[[object], str] = Field(exclude=True)
    completion_check: Optional[Callable[[], tuple[bool, object, Optional[str]]]] = Field(default=None, exclude=True)
    completion_check_retries: Optional[int]=5,
    transition_checks: list[Callable[[object], bool]] = Field(default_factory=list, exclude=True)

    def to_string(self, indent="\t") -> str:
        return f"{indent} - [{self.source}] {self.description}\n{indent} - targets: {self.targets}\n{indent} - checks={[c.__name__ for c in self.transition_checks]}\n{indent} - confirm={self.confirm_request}"

class Refinable(BaseModel):
  pass

class Refinement(BaseModel):
  id: Optional[str] = Field(default_factory=str, description="unique id for this refinement")
  source: str = Field(description="user or agent suggested")
  operation: Literal["add", "modify", "delete", "commit"]
  refinement_target_type: Literal["requirement", "generation_step", "validation_step", "refinement"]
  refinement_target_id: Optional[str] = Field(default_factory=str, description="id of item for suggested refinement")
  refinables_covered: list[str] = Field(default_factory=list, description="id of refinables covered by this refinement")
  text: Optional[str] = Field(description="suggested refinement")
  ordinal: Optional[float] = -1
  user_comment: Optional[str] = Field(description="user can request specific modification from agent")

  def __str__(self):
    return f"Refinement(id: {self.id} <ord:{self.ordinal}>, ({self.source}, op: {self.operation} target: {self.refinement_target_type}<{self.refinement_target_id}>): {self.text or ''}"        