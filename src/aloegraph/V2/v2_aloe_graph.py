# src/aloegraph/V2/v2_aloe_graph.py
"""
v2_aloe_graph
=============

- **Module:** `src/aloegraph/V2/v2_aloe_graph.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Concrete graph execution engine for AloeGraph V2.

This module defines `V2AloeGraph`, the primary class responsible for compiling
and executing declaratively defined node–edge graphs. It extends
`V2AloeNodeGraph` with lifecycle management, logging, and error handling.

Overview
--------
- **END constant**:
  Special marker string `"__END__"` used to signal termination of graph
  execution. Other control markers (RESUME, INTERRUPT, CONTINUE) are reserved
  but not currently active.

- **V2AloeGraph**:
  Provides methods to:
    * `compile` — validate nodes and edges, ensure a single entry node,
      build an execution plan, and generate a Mermaid chart.
    * `invoke` — execute the graph step by step, handling interrupts,
      recursion limits, and logging transitions.
    * `notify_log` — send messages to an optional `LogNotifier`.
    * `preflight` — hook for subclasses to run validation checks before
      compilation.
    * `set_state` — assign or update the current state object.

Lifecycle
---------
1. **Define** a subclass of `V2AloeGraph` with nodes and edges declared
   using decorators from `V2AloeNodeGraph`.
2. **Compile** the graph with `compile()`. This validates structure,
   sets the start node, and prepares the execution plan.
3. **Invoke** the graph with `invoke()`. The graph traverses nodes and
   edges until reaching `END` or encountering an interrupt.
4. **Log** messages are optionally sent to a `LogNotifier` for debugging
   and monitoring.

Example
-------
```python
class MyGraph(V2AloeGraph[v2_base_model.V2AloeConfig]):
    @V2AloeGraph.AloeNode(name="Start", is_entry=True)
    def start(self, state):
        state.__EDGE__ = "Next"
        return state

    @V2AloeGraph.AloeEdge(target="End", description="finish")
    def to_end(self, state):
        state.__EDGE__ = END
        return state

graph = MyGraph(initial_state=v2_base_model.V2AloeConfig())
plan = graph.compile()
final_state = graph.invoke()
```
"""

import aloegraph.V2.v2_base_model as v2_base_model
from aloegraph.V2.v2_base_model import END
import aloegraph.V2.graph.v2_aloe_node_graph as v2_aloe_node_graph

from aloegraph.V2.exception.base_exceptions import AloeGraphCompileError
import traceback

# RESUME = "__RESUME__"
# INTERRUPT = "__INTERRUPT__"
# CONTINUE = "__CONTINUE__"


class V2AloeGraph[StateT:v2_base_model.V2AloeConfig](v2_aloe_node_graph.V2AloeNodeGraph[StateT]):
    """
    Concrete graph class for AloeGraph V2.

    `V2AloeGraph` extends `V2AloeNodeGraph` to provide execution,
    compilation, and logging capabilities for declaratively defined
    node–edge graphs. It manages state transitions, handles interrupts,
    and can render execution plans and Mermaid diagrams.

    Type Parameters
    ---------------
    StateT : V2AloeConfig
        The type of the state object used to track graph execution.
    """
    def __init_subclass__(cls, **kwargs):
        """
        Hook called when a subclass of `V2AloeGraph` is defined.

        Ensures that node wrappers are collected and registered
        when subclasses are created.
        """
        super().__init_subclass__(**kwargs)

    def set_state(self, state: StateT):
        """
        Set the current graph state.

        Parameters
        ----------
        state : StateT
            The state object to assign to the graph.
        """
        self.state = state

    def __init__(self, initial_state: StateT = None, log_notifier: v2_base_model.LogNotifier = None,):
        """
        Initialize a new AloeGraph instance.

        Parameters
        ----------
        initial_state : StateT, optional
            Initial state object for the graph.
        log_notifier : LogNotifier, optional
            Optional notifier for logging graph events.
        """
        if initial_state:
            self.set_state(initial_state)

        if log_notifier:
            self.log_notifier: v2_base_model.LogNotifier = log_notifier

    def notify_log(self, message) -> None:
        """
        Send a log message to the configured notifier.

        Parameters
        ----------
        message : str
            The message to log.
        """
        if hasattr(self, "log_notifier"):
            self.log_notifier.add_log(f"{self.GraphName} | {message}")

    def invoke(self, state: StateT = None, recursion_limit=10) -> StateT:
        """
        Execute the graph starting from the entry node.

        Iteratively traverses nodes and edges until reaching the `END`
        marker or encountering an interrupt. Handles exceptions, logs
        transitions, and enforces a recursion limit.

        Parameters
        ----------
        state : StateT, optional
            State object to use for execution. If not provided, the
            existing state is used.
        recursion_limit : int, default 10
            Maximum number of steps allowed before raising an error.

        Returns
        -------
        StateT
            The final state object after execution.

        Raises
        ------
        RuntimeError
            If the graph has not been compiled or recursion limit is exceeded.
        ValueError
            If an edge target is undefined.
        """
        self.notify_log(f"[V2AloeGraph.invoke] Entering")
        if not self._is_initialized:
            raise RuntimeError("Graph has not been compiled")
        if state:
            self.state = state
        self.state._enter()
        if self.state.__INTERRUPT__:
            self.state.__EDGE__ = self.state.__INTERRUPT__
            self.state.__INTERRUPT__ = ""

            self.notify_log(
                f"[V2AloeGraph.invoke] __INTERRUPT__ Resuming <{self.state.__EDGE__}>")
        else:
            self.state.__EDGE__ = self.start_node
            self.notify_log(
                f"[V2AloeGraph.invoke] Calling Start Node <{self.state.__EDGE__}>")
        steps = 0
        try:
            while self.state.__EDGE__ != END and not self.state.__INTERRUPT__:
                node_fn = self.nodes[self.state.__EDGE__]
                prev_edge = self.state.__EDGE__
                self.notify_log(
                    f"[V2AloeGraph.invoke:{steps}] --- Entering <{self.state.__EDGE__}> ---")
                try:
                    self.state = node_fn(self, self.state)
                except Exception as e:
                    self.notify_log(
                        f"[V2AloeGraph.invoke:{steps}] --- EXCEPTION <{prev_edge}> ---\n\n{e}\n\n{traceback.format_exc()}")

                self.notify_log(
                    f"[V2AloeGraph.invoke:{steps}] --- Exiting <{prev_edge} -> {self.state.__EDGE__}> ---")
                next_edge = node_fn.edge_map[self.state.__EDGE__]
                if not next_edge:
                    if len(node_fn.edge_map) == 1:
                        next_edge = [e for e in node_fn.edge_map.values()][0]
                    else:
                        raise ValueError("state.__EDGE__ not defined")
                if next_edge.interrupt:
                    self.state.__INTERRUPT__ = self.state.__EDGE__
                    self.notify_log(
                        f"[V2AloeGraph.invoke:{steps}] __INTERRUPT__ Received <{self.state.__EDGE__}>")
                else:
                    self.state.__INTERRUPT__ = ""
                steps += 1
                if steps > recursion_limit:
                    self.notify_log(
                        f"[V2AloeGraph.invoke:{steps}] ERROR: Recursion limit {recursion_limit} reached without hitting END")
                    self.state.error_message = f"Recursion limit {recursion_limit} reached without hitting END"
                    raise RuntimeError(self.state.error_message)
        finally:
            self.state._exit()
            return self.state

    def preflight(self) -> bool:
        """
        Run preflight checks before compilation.

        Override this method in subclasses to implement custom validation
        logic. Called automatically during `compile`.

        Returns
        -------
        bool
            True if preflight checks pass, False otherwise.
        """
        return True

    def compile(self, graph_name: str = None, log_notifier: v2_base_model.LogNotifier = None, state: StateT = None) -> None:
        """
        Compile the graph definition.

        Validates nodes and edges, ensures a single entry node is defined,
        builds an execution plan, and prepares Mermaid chart rendering.
        Marks the graph as initialized for execution.

        Parameters
        ----------
        graph_name : str, optional
            Name of the graph. Defaults to the class name.
        log_notifier : LogNotifier, optional
            Optional notifier for logging graph events.
        state : StateT, optional
            Initial state object for the graph.

        Returns
        -------
        dict
            Execution plan mapping node names to their functions and targets.

        Raises
        ------
        AloeGraphCompileError
            If preflight checks fail.
        ValueError
            If edge targets are missing, or if no/too many start nodes are defined.
        """
        if not graph_name:
            self.GraphName = type(self).__name__

        if state:
            self.state = state

        if log_notifier:
            self.log_notifier = log_notifier

        if not self.preflight():
            AloeGraphCompileError("Preflight Checks Failed")

        for node_name, node_wrapper in self.nodes.items():
            for edge_name, edge_data in node_wrapper.edge_map.items():
                target = edge_data.target
                if target not in self.nodes and target not in [END]:
                    raise ValueError(
                        f"Edge<{edge_name}> ({node_name}->{target}): target not found in nodes")

        start_nodes = [
            node_name for node_name, value
            in self.nodes.items()
            if value.node_data.is_entry]

        if not start_nodes:
            raise ValueError("No start node defined")

        if len(start_nodes) > 1:
            raise ValueError("More than one start node defined")

        self.start_node = start_nodes[0]

        plan = {}
        for node_name, node_wrapper in self.nodes.items():
            plan[node_name] = {
                "func": node_name,
                "targets": [edge_data.target
                            for edge_name, edge_data
                            in node_wrapper.edge_map.items()]}

        self.mermaid_chart = self.render_mermaid_chart()
        self.execution_plan = plan
        self.start_nodes = start_nodes

        self._is_initialized = True

        print("Graph compiled successfully.")
        return plan
