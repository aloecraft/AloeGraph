from aloegraph.aloe_config import AloeConfig
from aloegraph.model.base_model import AloeEdge

from typing import Callable, Optional, Union, Optional
from functools import wraps
from abc import ABC, abstractmethod

END = "__END__"

def default_decider(state: AloeConfig) -> str:
    if state.desired_node and state.desired_node in state.get_available_transitions():
        return state.desired_node
    return END

class AloeGraphBase(ABC):

    @abstractmethod
    def __init__(self, initial_state: AloeConfig, agent_name: str, agent_description: str):
        pass

    @abstractmethod
    def invoke(self, state: AloeConfig, recursion_limit: int = 10) -> AloeConfig:
        pass

    @abstractmethod
    def AloeNode(
        self,
        targets: list[Union[str, Callable]],
        description: Optional[str] = "",
        recommended_next: Union[str, Callable] = None,
        confirm_request: Optional[str] = None,
        branch_decider: Optional[Callable[[AloeConfig], str]] = default_decider,
        transition_checks: Optional[list[Callable[[AloeConfig], bool]]] = None,
    ):
        pass

class AloeGraph(AloeGraphBase):

  def __init__(self, initial_state: AloeConfig, agent_name: str, agent_description: str):
    self.state = initial_state
    self.agent_name = agent_name
    self.agent_description = agent_description
    self.workflow = None

  def AloeNode(
      self,
      targets: list[Union[str, Callable]],
      description: Optional[str] = "",
      recommended_next: Union[str, Callable] = None,
      confirm_request: Optional[str] = None,
      branch_decider: Optional[Callable[[AloeConfig], str]] = default_decider,
      transition_checks: Optional[list[Callable[[AloeConfig], bool]]] = None,
  ):
      
      rec_name = None
      if recommended_next:
          rec_name = recommended_next if isinstance(recommended_next, str) else recommended_next.__name__

      desc = description

      def decorator(f: Callable) -> Callable:
          source_name = f.__name__
          target_names = [t if isinstance(t, str) else t.__name__ for t in targets]

          edge = AloeEdge(
              source=source_name,
              targets=target_names,
              description=desc,
              recommended_next=rec_name,
              confirm_request=confirm_request,
              branch_decider=branch_decider,  # see router below
              transition_checks=transition_checks or [],
          )

          @wraps(f)
          def wrapper(state: AloeConfig, *args, **kwargs):
              state.current_node = source_name

              if source_name == state.desired_node:
                  state.desired_node = ""

              state.DEBUG_node_visits.append(source_name)
              return f(state, *args, **kwargs)

          # Register
          self.state.edges[source_name] = edge
          self.state.nodes[source_name] = wrapper
          return wrapper

      return decorator

  def invoke(self, state: AloeConfig, recursion_limit: int = 10) -> AloeConfig:
        
        steps = 0
        while steps < recursion_limit:
            steps += 1

            if state.desired_node and state.desired_node in state.get_available_transitions():
                state.current_node = state.desired_node
                state.desired_node = ""

            current = state.current_node

            # Run the node
            node_fn = state.nodes[current]
            state = node_fn(state)

            # Decide where to go next
            edge = state.edges[current]

            next_node = None
            if edge.branch_decider:
                branch_decider_result = edge.branch_decider(state)
                next_node = branch_decider_result
            else:
                next_node =  None

            # If END, stop
            if next_node == END or next_node is None:
                return state

            # Check transition conditions
            if next_node not in edge.targets:
                raise ValueError(f"Invalid transition: {current} -> {next_node}")

            # Advance
            state.current_node = next_node

        raise RuntimeError(f"Recursion limit {recursion_limit} reached without hitting END")