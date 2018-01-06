"""Provide useful and simple classes to manage Directed and Undirected graphs.

Provide useful and simple classes to manage Directed and Undirected graphs. It contains the six classes
`UndirectedGraph`, `UndirectedNode`, `Edge`, `DirectedGraph`, `DirectedNode` and `Arc`.

The reason why there are six classes instead of three modeling at the same time the Undirected and the directed case is
only a mater of terminology. We talk about edges and neighbors in the undirected case, and we talk about arcs, input
arcs, output arcs, input neighbor, ... in the directed case. Thus, the directed classes are mostly the same as the
undirected ones where every method or property is tripled. The good point is that the name of the methods are consistent
with the used case (directed or undirected).

To build a graph, use the graph classes. It is not recommended to manually instantiate a node, an edge or an arc as it
is not possible to link them with the graph objects. The graph classes have methods to manage the nodes and the links
of the graphs.
"""

__all__ = ['directedgraph', 'undirectedgraph']
