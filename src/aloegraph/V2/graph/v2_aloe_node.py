# src/aloegraph/V2/graph/v2_aloe_node.py
"""
v2_aloe_node (aloe_node_wrapper)
=================

- **Module:** `src/aloegraph/V2/graph/v2_aloe_node.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Core utilities for wrapping functions as nodes and edges in AloeGraph V2.

This module provides the `AloeNodeWrapper` class and the `AloeNode` /
`AloeEdge` decorators, which together enable declarative graph construction.
Functions decorated with `@AloeNode` or `@AloeEdge` are automatically wrapped
with metadata describing their role in the graph, making them discoverable
and executable by `V2AloeGraph`.

Overview
--------
- **AloeNodeWrapper**:
  Encapsulates a function and attaches metadata (`AloeNodeData` or
  `AloeEdgeData`). Supports binding functions to instances, direct invocation,
  and static helpers for wrapping nodes and edges.

- **AloeNode decorator**:
  Marks a function as a graph node. Attaches `AloeNodeData` including name,
  description, entry status, and render shape.

- **AloeEdge decorator**:
  Marks a function as a graph edge. Attaches `AloeEdgeData` including target,
  label, description, and interrupt flag.

Responsibilities
----------------
- Enforce initialization rules (prevent re‑initializing nodes or duplicate edges).
- Provide a consistent schema for nodes and edges in AloeGraph.
- Allow declarative graph definitions by simply decorating functions.

Usage
-----
Define nodes and edges in a subclass of `V2AloeGraph`:

```python
from aloegraph.V2.graph.aloe_node_wrapper import AloeNode, AloeEdge

class MyGraph(V2AloeGraph[V2AloeConfig]):
    @AloeNode(name="Start", is_entry=True)
    def start(self, state):
        state.__EDGE__ = "Next"
        return state

    @AloeEdge(target="End", description="finish")
    def to_end(self, state):
        state.__EDGE__ = "__END__"
        return state
```        
"""

import aloegraph.V2.v2_base_model as v2_base_model
from typing import Callable

class AloeNodeWrapper(Callable):
    """
    Wrapper class for functions decorated as AloeGraph nodes or edges.

    This class encapsulates a function and attaches metadata describing
    its role in the graph. It supports both node and edge definitions,
    storing associated `AloeNodeData` and `AloeEdgeData`.

    Responsibilities
    ----------------
    - Bind the wrapped function to an instance when accessed as a method.
    - Allow direct invocation of the wrapped function via `__call__`.
    - Provide static helpers (`wrap_node`, `wrap_edge`) to attach metadata
      and enforce initialization rules.

    Attributes
    ----------
    node_data : AloeNodeData
        Metadata describing the node (name, description, entry status, render shape).
    edge_map : dict[str, AloeEdgeData]
        Mapping of edge names to edge metadata for outgoing edges.
    fn : Callable
        The original function being wrapped.
    """    
    def __init__(self, fn: Callable):
        self.node_data: v2_base_model.AloeNodeData=v2_base_model.AloeNodeData()
        self.edge_map: dict[str,v2_base_model.AloeEdgeData]={}
        self.fn = fn

    def __get__(self, instance, owner):
        """
        Bind the wrapped function to the given instance.

        Parameters
        ----------
        instance : Any
            The object instance to bind the function to.
        owner : type
            The class owning the function.

        Returns
        -------
        Callable
            A bound function that passes `instance` as the first argument.
        """
        return lambda *args, **kwargs: self.fn(instance, *args, **kwargs)
    
    def __call__(self, *args, **kwargs):
        """
        Invoke the wrapped function directly.

        Parameters
        ----------
        *args : tuple
            Positional arguments to pass to the function.
        **kwargs : dict
            Keyword arguments to pass to the function.

        Returns
        -------
        Any
            The result of calling the wrapped function.
        """        
        return self.fn(*args, **kwargs)
    
    @staticmethod
    def wrap_edge(fn: Callable, target:str, name:str=None, description:str=None, interrupt:bool=False):
        """
        Wrap a function as an AloeGraph edge.

        Creates or reuses an `AloeNodeWrapper` and attaches an `AloeEdgeData`
        entry describing the edge.

        Parameters
        ----------
        fn : Callable
            The function to wrap.
        target : str
            The target node name this edge points to.
        name : str, optional
            The label for the edge. Defaults to the target name.
        description : str, optional
            Human-readable description of the edge.
        interrupt : bool, default False
            Whether this edge represents an interrupt in the graph flow.

        Returns
        -------
        AloeNodeWrapper
            The wrapper with the edge metadata attached.

        Raises
        ------
        TypeError
            If the target is empty or an edge with the same name already exists.
        """        
        node_wrapper = fn if isinstance(fn, AloeNodeWrapper) else AloeNodeWrapper(fn)
        edge_name = name or target
        if not target:
            raise TypeError(f"AloeEdge target must not be empty")
        if edge_name in node_wrapper.edge_map:
            raise TypeError(f"AloeEdge with name '{edge_name}' already added to this node")
        node_wrapper.edge_map[edge_name] = v2_base_model.AloeEdgeData(target=target, name=edge_name, description=description, interrupt=interrupt)
        return node_wrapper

    @staticmethod
    def wrap_node(fn: Callable, name:str=None, description:str=None, is_entry:bool=False, node_render_shape: v2_base_model.NodeRenderShape = v2_base_model.NodeRenderShape.SQUARE):
        """
        Wrap a function as an AloeGraph node.

        Creates or reuses an `AloeNodeWrapper` and attaches `AloeNodeData`
        describing the node.

        Parameters
        ----------
        fn : Callable
            The function to wrap.
        name : str, optional
            The name of the node. Defaults to the function name.
        description : str, optional
            Human-readable description of the node.
        is_entry : bool, default False
            Whether this node is the entry point of the graph.
        node_render_shape : NodeRenderShape, default SQUARE
            The visual shape used when rendering the node in diagrams.

        Returns
        -------
        AloeNodeWrapper
            The wrapper with the node metadata attached.

        Raises
        ------
        TypeError
            If the node has already been initialized.
        """        
        node_wrapper = fn if isinstance(fn, AloeNodeWrapper) else AloeNodeWrapper(fn)
        if node_wrapper.node_data._is_initialized:
            raise TypeError("Attempting to reinitialize AloeNode")
        node_name = name or node_wrapper.fn.__name__
        node_wrapper.node_data._is_initialized = True
        node_wrapper.node_data.name = node_name
        node_wrapper.node_data.description = description
        node_wrapper.node_data.is_entry = is_entry
        node_wrapper.node_data.node_render_shape = node_render_shape
        return node_wrapper

def AloeNode(name:str=None, description:str=None, is_entry:bool=False, node_render_shape: v2_base_model.NodeRenderShape = v2_base_model.NodeRenderShape.SQUARE):
    """
    Decorator for defining an AloeGraph node.

    Wraps a function in an `AloeNodeWrapper` and attaches node metadata.

    Parameters
    ----------
    name : str, optional
        The name of the node. Defaults to the function name.
    description : str, optional
        Human-readable description of the node.
    is_entry : bool, default False
        Whether this node is the entry point of the graph.
    node_render_shape : NodeRenderShape, default SQUARE
        The visual shape used when rendering the node in diagrams.

    Returns
    -------
    Callable
        A decorator that wraps the function as a node.
    """    
    def decorator(fn: Callable):
        return AloeNodeWrapper.wrap_node(fn, name, description, is_entry, node_render_shape)
    return decorator

def AloeEdge(target:str, name:str=None, description:str=None, interrupt:bool=False):
    """
    Decorator for defining an AloeGraph edge.

    Wraps a function in an `AloeNodeWrapper` and attaches edge metadata.

    Parameters
    ----------
    target : str
        The target node name this edge points to.
    name : str, optional
        The label for the edge. Defaults to the target name.
    description : str, optional
        Human-readable description of the edge.
    interrupt : bool, default False
        Whether this edge represents an interrupt in the graph flow.

    Returns
    -------
    Callable
        A decorator that wraps the function as an edge.
    """    
    def decorator(fn: Callable):
        return AloeNodeWrapper.wrap_edge(fn, target, name, description, interrupt)
    return decorator