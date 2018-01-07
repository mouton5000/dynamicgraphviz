"""Provide useful and simple classes to manage Undirected graphs.

Provide useful and simple classes to manage Undirected graphs. It contains the three classes
`UndirectedGraph`, `UndirectedNode` and `Edge`.

To build a graph, use the `UndirectedGraph` class. It is not recommended to manually instantiate a node, an edge as it
is not possible to link them with the graph objects. The graph classes has methods to manage the nodes and the edges
of the graphs.
"""


from dynamicgraphviz.graph.graph import _Graph, _Node, _Link
from dynamicgraphviz.exceptions.graph_errors import *

__author__ = "Dimitri Watel"
__copyright__ = "Copyright 2018, dynamicgraphviz"

class UndirectedGraph(_Graph):
    """Undirected graphs.

    This class represents undirected graphs (sets of vertices (or nodes) connected by edges,
    see https://en.wikipedia.org/wiki/Graph_theory for basic definitions). It contains four
    methods to simply edit the graph: `add_node`, `remove_node`, `add_edge` and `remove_edge` and two properties,
    `nodes` and `edges`, to respectively access to the nodes and the edges of the graph.

    The graphs are simple: there are no two edges between the same two nodes and there is no loop.

    For a graph g, it is possible to use
    - len(g) to get the number of node of g
    - str(g) to get a printable representation of the graph
    - iter(g) to get an iterator over the nodes of g (or 'for node in g:')
    - 'node in g' to know if a node is in g.

    WARNING : The graph should be edited only with the methods `add_node`, `remove_node, `add_edge`, and `remove_edge`
    otherwise an unexpected behaviour may occurs.

    """

    def __init__(self):
        super().__init__(directed=False)

    def _build_node(self):
        return UndirectedNode(self)

    def _build_link(self, u, v):
        return Edge(u, v), UndirectedNode._add_incident_edge

    @property
    def edges(self):
        """Return an iterator through the list of edges of the graph"""
        return super().links

    def add_edge(self, u, v):
        """Add an edge to the graph and return it.

        Add an edge between the nodes u and v of the graph. The nodes u and v should belong to the graph and not be
        equal, and there should not be already an edge between u and v, otherwise an exception is raised.
        :param u: a node of the graph
        :param v: a node of the graph, distinct from u
        :return: a new edge linking u and v.
        :raises TypeError: if u or v is not a node
        :raises NodeMembershipError: if the node u or the node v does not belong to the graph
        :raises GraphError: if the node u equals the node v
        :raises LinkError: if there is already an edge between u and v.
        """
        return super()._add_link(u, v)

    def remove_edge(self, e):
        """Remove an edge e of the graph.

        Remove the edge e of the graph. That edge should belong to the graph, otherwise an exception is raised.

        :param e: an edge of the graph that should be removed.
        :raises TypeError: if e is not an edge
        :raises LinkMembershipError: if the edge e does not belong to the graph.
        """
        return self._remove_link(e)

    def __str__(self):
        return '\n'.join(' '.join([('1' if node2.is_neighbor_of(node) else '0') for node2 in self]) for node in self)


class UndirectedNode(_Node):
    """Vertice (or node) of an undirected graph.

    This class represents any node of an undirected graph. This class should not be manually instantiated. Use
    the method `UndirectedGraph.add_node` instead. Otherwise an unexpected behaviour may occurs.

    With this class, it is possible to access to all the incident edges and to the corresponding neighbors of the node.
    - the property `nb_neighbors` and `len(self)` return the number of neighbors.
    - the property `neighbors` and the method `is_neighbor_of` give access to the neighbors.
    - the property `incident_edges` and the methods `get_incident_edge` and `is_incident_to` give access to the
    incident_edges.

    Moreover, a node has a unique index that can be used to easily identify that node and that is used when the node
    is printed with `str`. That index is accessible with the property `index`.
    """

    def __init__(self, g):
        """Build a new node of the undirected graph g."""
        super().__init__(g)
        self.__edges = {}

    def __len__(self):
        """Return the number of neighbors of the node."""
        return self.nb_neighbors

    @property
    def nb_neighbors(self):
        """Return the number of neighbors of the node."""
        return len(self.__edges)

    @property
    def neighbors(self):
        """Return an iterator through the list of neighbor nodes of the node."""
        return iter(self.__edges.keys())

    def is_neighbor_of(self, v):
        """Return True if v is a neighbor of this node and False otherwise."""
        return v in self.__edges

    def _remove_neighbor(self, v):
        """Remove the node v from the list of neighbors of the node.

        If the node v is not a neighbor of the node, an exception is raised.

        :param v: the neighbor to be removed
        :raises TypeError: if v is not a node of an undirected graph
        :raises NodeError: if v is not a neighbor of the node
        """
        try:
            del self.__edges[v]
        except KeyError:
            if isinstance(v, UndirectedNode):
                raise NodeError(self.__graph, self, 'The node ' + str(v) + ' is not a neighbor of this node.')
            else:
                raise TypeError()

    @property
    def incident_edges(self):
        """Return an iterator through the list of incident edges of the node."""
        return iter(self.__edges.values())

    def get_incident_edge(self, v):
        """Return the edge between this node and the node v."""
        return self.__edges[v]

    def is_incident_to(self, e):
        """Return True if the node is incident to the edge e and False otherwise."""
        return super().is_incident_to(e)

    def _add_incident_edge(self, e):
        """Add the edge e to the list of incident edges of this node (and the corresponding neighbor to the list
        of neighbors).

        Add the edge e to the list of incident edges of this node (and the corresponding neighbor to the list
        of neighbors). If the node is not an extremity of e, an exception is raised. If e is not an edge,
        an unexpected behaviour may occurs.

        :param e: the edge to be added.
        :raises TypeError: if e is not an edge.
        :raises LinkError: if the node is not an extremity of e.
        """
        try:
            v = e.neighbor(self)
            if v is not None:
                self.__edges[v] = e
            else:
                if not isinstance(e, Edge):
                    raise TypeError()
                else:
                    raise LinkError(self.__graph, e, str(self) + ' is not one of the extremities.')
        except AttributeError:
            if not isinstance(e, Edge):
                raise TypeError()
            else:
                raise

    def _remove_incident_edge(self, e):
        """Remove the edge e from the list of incident edges of this node (and the corresponding neighbor from the list
        of neighbors).

        Remove the edge e from the list of incident edges of this node (and the corresponding neighbor from the list
        of neighbors). If the node is not an extremity of e, an exception is raised.

        :param e: the edge to be removed.
        :raises TypeError: if e is not an edge.
        :raises LinkError: if the node is not an extremity of e.
        """
        try:
            v = e.neighbor(self)
            if v is not None:
                self._remove_neighbor(v)
            else:
                if not isinstance(e, Edge):
                    raise TypeError()
                else:
                    raise LinkError(self.__graph, e, str(self) + ' is not one of the extremities.')
        except AttributeError:
            if not isinstance(e, Edge):
                raise TypeError()
            else:
                raise


class Edge(_Link):
    """Undirected edge.

    This class represents any edge of an undirected graph. This class should not be manually
    instantiated. Use the methods `UndirectedGraph.add_edge` instead. Otherwise, unexpected
    behaviour may occurs.

    With this class, it is possible to access to the extremities of the edge with the property
    `extremities`. In addition, given one of the two extremities, it is possible to retrieve the other with the method
    `neighbor`. Finally the property `directed` can be used if it is not known if this link is an edge or an arc. In
    this case, it always returns False.
    """

    @property
    def extremities(self):
        """Return the two extremities of the edge."""
        return super().extremities

    def neighbor(self, v):
        """Return the extremity of the edge not equal to v or None if v is not an extremity.

        :param v: an extremity of the edge
        :return: the extremity not equal to v or None if v is not an extremity.
        """
        return super().neighbor(v)

    @property
    def directed(self):
        """Return False. Use this method if it is not clear that this object is an edge or an arc. Equivalent to
        `not isinstance(self, Arc)`"""
        return False
