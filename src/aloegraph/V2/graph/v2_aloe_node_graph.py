# src/aloegraph/V2/graph/v2_aloe_node_graph.py
"""
v2_aloe_node_graph
=============

- **Module:** `src/aloegraph/V2/graph/v2_aloe_node_graph.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Defines the abstract base class `V2AloeNodeGraph` for constructing declarative
node–edge graphs in AloeGraph V2. This module provides decorators for
annotating Python functions as graph nodes or edges, automatically collecting
them into a graph structure, and rendering the resulting graph as a Mermaid
diagram.

Overview
--------
- **V2AloeNodeGraph**:
  Abstract base class for graph definitions. Subclasses declare nodes and edges
  using decorators, and the class machinery collects them into a `nodes` map
  at initialization.

- **AloeNode decorator**:
  Marks a function as a graph node. Each node has metadata such as name,
  description, entry status, and render shape (see `NodeRenderShape`).

- **AloeEdge decorator**:
  Marks a function as a graph edge. Each edge connects a source node to a
  target node, with optional label, description, and interrupt flag.

- **Mermaid rendering utilities**:
  `generate_mermaid_chart` builds Mermaid syntax for the graph, while
  `render_mermaid_chart` and `mermaid_chart_png` produce visual diagrams
  for interactive display or export.

Usage
-----
Subclass `V2AloeNodeGraph` and decorate methods with `@AloeNode` and `@AloeEdge`
to define the graph declaratively. The graph can then be rendered to Mermaid
syntax or exported as a PNG for visualization.

Example
-------
```python
class MyGraph(V2AloeNodeGraph[str]):
    @V2AloeNodeGraph.AloeNode(name="Start", is_entry=True)
    def start(self, state: str):
        ...

    @V2AloeNodeGraph.AloeEdge(target="End", description="finish")
    def to_end(self, state: str):
        ...

graph = MyGraph(initial_state="ready")
print(graph.generate_mermaid_chart())
```
"""

import aloegraph.V2.v2_base_model as v2_base_model
import aloegraph.V2.graph.v2_aloe_node as v2_aloe_node
from aloegraph.V2.v2_base_model import END

import mermaid as md
from mermaid.graph import Graph
from abc import ABC, abstractmethod
from typing import Callable


class V2AloeNodeGraph[StateT](ABC):
    """
    Abstract base class for defining AloeGraph node graphs.

    This class provides decorators for declaring nodes and edges in a graph,
    manages initialization of node wrappers, and includes utilities for
    rendering the graph as a Mermaid diagram.

    Type Parameters
    ---------------
    StateT : Any
        The type of the initial state object used to configure the graph.
    """

    def AloeEdge(self, target: str, name: str = None, description: str = None, interrupt: bool = False):
        """
        Decorator for defining an edge between nodes.

        Wraps a function as an `AloeEdge` that connects the current node
        to a target node.

        Parameters
        ----------
        target : str
            The name of the target node.
        name : str, optional
            The label or identifier for the edge.
        description : str, optional
            Human-readable description of the edge.
        interrupt : bool, default False
            Whether this edge represents an interrupt in the graph flow.

        Returns
        -------
        Callable
            A decorator that wraps the function as an edge.
        """
        self._is_initialized = False

        def decorator(fn: Callable):
            node_wrapper = v2_aloe_node.AloeNodeWrapper.wrap_edge(
                fn, target, name, description, interrupt)
            return node_wrapper
        return decorator

    def AloeNode(self, name: str = None, description: str = None, is_entry: bool = False, node_render_shape: v2_base_model.NodeRenderShape = v2_base_model.NodeRenderShape.SQUARE):
        """
        Decorator for defining a node in the graph.

        Wraps a function as an `AloeNode` with associated metadata such as
        name, description, entry status, and render shape.

        Parameters
        ----------
        name : str, optional
            The name of the node.
        description : str, optional
            Human-readable description of the node.
        is_entry : bool, default False
            Whether this node is the entry point of the graph.
        node_render_shape : NodeRenderShape, default SQUARE
            The visual shape used when rendering the node in Mermaid diagrams.

        Returns
        -------
        Callable
            A decorator that wraps the function as a node.
        """
        self._is_initialized = False

        def decorator(fn: Callable):
            node_wrapper = v2_aloe_node.AloeNodeWrapper.wrap_node(
                fn, name, description, is_entry, node_render_shape)
            self.nodes[node_wrapper.node_data.name] = node_wrapper
            return node_wrapper
        return decorator

    @abstractmethod
    def __init__(self, initial_state: StateT, *args, **kwargs):
        """
        Abstract initializer for the graph.

        Subclasses must implement this to set up the initial state and
        any additional configuration.

        Parameters
        ----------
        initial_state : StateT
            The initial state object for the graph.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.
        """
        pass

    def __init_subclass__(cls, **kwargs):
        """
        Hook called when a subclass is defined.

        Collects all `AloeNodeWrapper` instances declared in the subclass
        and registers them as nodes. Wraps the subclass initializer to
        attach the node map and initial state.
        """
        super().__init_subclass__(**kwargs)
        nodes = {}
        for class_name, class_method in cls.__dict__.items():
            if isinstance(class_method, v2_aloe_node.AloeNodeWrapper):
                setattr(cls, class_name, class_method)
                nodes[class_method.node_data.name] = class_method
        original_init = cls.__init__

        def wrapped_init(self, initial_state: StateT, *args, **kwargs):
            self._is_initialized = False
            self.nodes = nodes
            self.state = initial_state
            self.GraphName = ""
            if callable(original_init):
                original_init(self, self.state, *args, **kwargs)
        cls.__init__ = wrapped_init

    def generate_mermaid_chart(graph) -> str:
        """
        Generate a Mermaid diagram definition for the graph.

        Iterates over nodes and edges to produce Mermaid syntax that
        can be rendered into a flowchart.

        Parameters
        ----------
        graph : V2AloeNodeGraph
            The graph instance containing nodes and edges.

        Returns
        -------
        str
            Mermaid syntax representing the graph.
        """
        lines = ["graph"]

        # Add Nodes
        for name, node_wrapper in graph.nodes.items():
            node_data = node_wrapper.node_data
            label = node_data.name
            description = node_data.description
            is_entry = node_data.is_entry
            node_contents = node_data.node_render_shape.format(
                f"{label}{(': '+description) if description else ''}")
            line = f"{('__START__' + v2_base_model.NodeRenderShape.STADIUM.format('__START__') + f' --> ')
                      if is_entry else ''}" + f"{label}{node_contents}"
            lines.append(line)

        # Add Edges
        for node_name, node_wrapper in graph.nodes.items():
            for edge_name, edge_data in node_wrapper.edge_map.items():
                target = edge_data.target
                label = edge_data.description

                if target == END:
                    lines.append(
                        f'{node_name} --> {END}{v2_base_model.NodeRenderShape.STADIUM.format(END)}')
                else:
                    if label:
                        lines.append(f'{node_name} -->|{label}| {target}')
                    else:
                        lines.append(f'{node_name} --> {target}')

        return "\n".join(lines)

    def render_mermaid_chart(self):
        """
        Render the graph as a Mermaid diagram object.

        Uses the generated Mermaid syntax to create a `Graph` and wrap
        it in a `Mermaid` object for display.

        Returns
        -------
        Mermaid
            A Mermaid diagram object representing the graph.
        """
        mermaid_syntax = self.generate_mermaid_chart()
        graph = Graph('My-AloeGraph', mermaid_syntax)
        return md.Mermaid(graph)

    def mermaid_chart_png(self, path):
        """
        Export the graph as a PNG image.

        Generates Mermaid syntax, renders the graph, and saves it to
        the specified file path.

        Parameters
        ----------
        path : str
            The file path where the PNG image will be saved.
        """
        mermaid_syntax = self.generate_mermaid_chart()
        graph = Graph('My-AloeGraph', mermaid_syntax)
        render = md.Mermaid(graph)
        render.to_png(path=path)
