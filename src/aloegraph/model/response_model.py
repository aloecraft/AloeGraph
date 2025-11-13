"""
- **Module:** `src/aloegraph/model/response_model.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)
"""

from pydantic import BaseModel, Field
from typing import Optional

from aloegraph.model.base_model import Refinable, Refinement


class BaseAloeAgentResponse(BaseModel):
    agent_message: str
    error_message: Optional[str]
    success: bool = True


class AloeIntakeResponse(BaseModel):
    target_node: Optional[str]
    agent_message: str


class IntakeAgentResponse(BaseAloeAgentResponse):
    target_node: Optional[str] = None


class StartNodeResponse(BaseAloeAgentResponse):
    project_description: Optional[str] = None


class RefinableAloeAgentNodeResponse(BaseAloeAgentResponse):
    refinements: list[Refinement] = Field(default_factory=list)
    list_items: Optional[bool] = False
