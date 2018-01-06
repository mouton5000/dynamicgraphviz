"""Provide useful and simple classes to manage Directed graphs.

Provide useful and simple classes to manage Directed graphs. It contains the three classes
`DirectedGraph`, `DirectedNode` and `Arc`.

To build a graph, use the `DirectedGraph` class. It is not recommended to manually instantiate a node, an arc as it
is not possible to link them with the graph objects. The graph class has methods to manage the nodes and the arcs
of the graphs.
"""

__author__ = "Dimitri Watel"
__copyright__ = "Copyright 2018, dynamicgraphviz"
__credits__ = ["Dimitri Watel"]
__license__ = "MIT"
__version__ = "0.99"
__maintainer__ = "Dimitri Watel"
__email__ = "patatemouton@gmail.com"
__status__ = "Development"


from graph.graph import _Graph, _Node, _Link
from itertools import chain
from exceptions.graph_errors import *


class DirectedGraph(_Graph):
    """Directed graphs.

    This class represents directed graphs (sets of vertices (or nodes) connected by arcs,
    see https://en.wikipedia.org/wiki/Graph_theory for basic definitions). It contains four
    methods to simply edit the graph: `add_node`, `remove_node`, `add_arc` and `remove_arc` and two properties,
    `nodes`, `arcs` to respectively access to the nodes and the arcs of the graph.

    The graphs are simple: there are no two arcs with the same input and output nodes and there is no loop. However
    there may be an arc from a node u to a node v and conversely an arc from v to u.

    For a graph g, it is possible to use
    - len(g) to get the number of node of g
    - str(g) to get a printable representation of the graph
    - iter(g) to get an iterator over the nodes of g (or 'for node in g:')
    - 'node in g' to know if a node is in g.

    WARNING : The graph should be edited only with the methods `add_node`, `remove_node, `add_arc`, and `remove_arc`
    otherwise an unexpected behaviour may occurs.
    """

    def __init__(self):
        super().__init__(directed=True)

    def _build_node(self):
        return DirectedNode(self)

    def _build_link(self, u, v):
        return Arc(u, v), DirectedNode._add_incident_arc

    @property
    def arcs(self):
        """Return an iterator through the list of arcs of the graph"""
        return super().links

    def add_arc(self, u, v):
        """Add an arc to the graph from the node u to the node v and return it.

        Add an arc from the node u to the node v of the graph. The nodes u and v should belong to the graph and not be
        equal, and there should not be already an arc from u to v, otherwise an exception is raised.
        :param u: a node of the graph
        :param v: a node of the graph, distinct from u
        :return: a new arc from u to v.
        :raises TypeError: if u or v is not a node
        :raises NodeMembershipError: if the node u or the node v does not belong to the graph
        :raises GraphError: if the node u equals the node v
        :raises LinkError: if there is already an arc from u to v.
        """
        return super()._add_link(u, v)

    def remove_arc(self, a):
        """Remove an arc of the graph.

        Remove the arc a of the graph. That arc should belong to the graph, otherwise an exception is raised.

        :param a: an arc of the graph that should be removed.
        :raises TypeError: if a is not an arc
        :raises LinkMembershipError: if the arc a does not belong to the graph.
        """
        return self._remove_link(a)

    def __str__(self):
        return '\n'.join(' '.join([('1' if node2.is_output_neighbor_of(node) else '0') for node2 in self]) for node
                         in self)


class DirectedNode(_Node):
    """Vertice (or node) of a directed graph.

    This class represents any node of a directed graph. This class should not be manually instantiated. Use
    the method `DirectedGraph.add_node` instead. Otherwise an unexpected behaviour may occurs.

    With this class, it is possible to access to all the incident arcs and to the corresponding neighbors of the node.
    - the property `neighbors`, `input_neighbors` and `output_neighbors` and the methods `is_neighbor_of`,
    `is_input_neighbor_of` and `is_output_neighbor_of` give access to the neighbors
    - the properties `incident_arcs`, `incident_input_arcs` and `incident_output_arcs` and the methods
    `get_incident_arcs`, `get_input_arc`, `get_output_arc`, `is_incident_to`, `is_input_arc` and `is_output_arc` give
    access to the incident_arcs.

    Moreover, a node has a unique index that can be used to easily identify that node and that is used when the node
    is printed with `str`. That index is accessible with the property `index`.
    """

    def __init__(self, g):
        """Build a new node of the directed graph g."""
        super().__init__(g)
        self.__input_arcs = {}
        self.__output_arcs = {}

    @property
    def input_neighbors(self):
        """Return an iterator through the list of input neighbor nodes of the node."""
        return iter(self.__input_arcs.keys())

    @property
    def output_neighbors(self):
        """Return an iterator through the list of output neighbor nodes of the node."""
        return iter(self.__output_arcs.keys())

    @property
    def neighbors(self):
        """Return an iterator through the list of input and output neighbor nodes of the node."""
        return chain(self.input_neighbors, self.output_neighbors)

    def is_input_neighbor_of(self, v):
        """Return True if this node is an input neighbor of this node (in other words, v is an output neighbor of this
        node, there is an arc from this node to v) and False otherwise."""
        return v in self.__output_arcs

    def is_output_neighbor_of(self, v):
        """Return True if this node is an output neighbor of this node (in other words, v is an input neighbor of this
        node, there is an arc from v to this node) and False otherwise."""
        return v in self.__input_arcs

    def is_neighbor_of(self, v):
        """Return True if this node is an input or an output neighbor of this node and False otherwise."""
        return self.is_input_neighbor_of(v) or self.is_output_neighbor_of(v)

    def _remove_neighbor(self, v):
        """Remove the node v from the list of neighbors of the node.

        Remove the node v from the list of neighbors of the node.
        If the node v is not a neighbor of the node, an exception is raised.

        :param v: the neighbor to be removed
        :raises TypeError: if v is not a node of an directed graph
        :raises NodeError: if v is not a neighbor of the node
        """
        try:
            del self.__input_arcs[v]
        except KeyError:
            try:
                del self.__output_arcs[v]
            except KeyError:
                if isinstance(v, DirectedGraph):
                    raise NodeError(self.__graph, self, 'The node ' + str(v) + ' is not a neighbor of this node.')
                else:
                    raise TypeError()

    @property
    def input_arcs(self):
        """Return an iterator through the list of input arcs of the node."""
        return iter(self.__input_arcs.values())

    @property
    def output_arcs(self):
        """Return an iterator through the list of output arcs of the node."""
        return iter(self.__output_arcs.values())

    @property
    def incident_arcs(self):
        """Return an iterator through the list of incident edges of the node."""
        return chain(self.output_arcs, self.input_arcs)

    def get_input_arc(self, v):
        """Return the arc from the node v to this node."""
        try:
            return self.__input_arcs[v]
        except KeyError:
            return None

    def get_output_arc(self, v):
        """Return the arc from this node to the node v."""
        try:
            return self.__output_arcs[v]
        except KeyError:
            return None

    def get_incident_arc(self, v):
        """Return the edge between this node and the node v."""
        a = self.get_input_arc(v)
        if a is None:
            a = self.get_output_arc(v)
        return a

    def is_input_arc(self, a):
        """Return True if the arc a enters the node and False otherwise."""
        return self == a.output_node

    def is_output_arc(self, a):
        """Return True if the arc a goes out of the node and False otherwise."""
        return self == a.input_node

    def is_incident_to(self, a):
        """Return True if the node is incident to the arc a and False otherwise."""
        return super().is_incident_to(a)

    def _add_incident_arc(self, a):
        """Add the arc a to the list of input or output arcs of this node (and the corresponding neighbor to the list
        of neighbors) depending whether the node is the input or the output node of a.

        Add the arc a to the list of input or output arcs of this node (and the corresponding neighbor to the list
        of neighbors) depending whether the node is the input or the output node of a. If the node is not an extremity
        of a, an exception is raised. If a is not an arc, an unexpected behaviour may occurs.

        :param a: the arc to be added.
        :raises TypeError: if a is not an arc.
        :raises LinkError: if the node is not an extremity of a.
        """

        try:
            u, v = a.extremities
            if u == self:
                self.__output_arcs[v] = a
            elif v == self:
                self.__input_arcs[u] = a
            else:
                if not isinstance(a, Arc):
                    raise TypeError()
                else:
                    raise LinkError(self.__graph, a, str(self) + ' is not one of the extremities.')
        except AttributeError:
            if not isinstance(a, Arc):
                raise TypeError()
            else:
                raise

    def _remove_incident_arc(self, a):
        """Remove the arc a from the list of input or output arcs of this node (and the corresponding neighbor from
        the list of neighbors) depending whether the node is the input or the output node of a.

        Remove the arc a from the list of input or output arcs of this node (and the corresponding neighbor from
        the list of neighbors) depending whether the node is the input or the output node of a. If the node is not an
        extremity of a, an exception is raised.

        :param a: the arc to be removed.
        :raises TypeError: if a is not an arc.
        :raises LinkError: if the node is not an extremity of a.
        """

        try:
            v = a.neighbor(self)
            if v is not None:
                self._remove_neighbor(v)
            else:
                if not isinstance(a, Arc):
                    raise TypeError()
                else:
                    raise LinkError(self.__graph, a, str(self) + ' is not one of the extremities.')
        except AttributeError:
            if not isinstance(a, Arc):
                raise TypeError()
            else:
                raise


class Arc(_Link):
    """Directed arc.

    This class represents any arc of a directed graph. This class should not be manually
    instantiated. Use the methods `DirectedGraph.add_arc` instead. Otherwise, unexpected
    behaviour may occurs.

    With this class, it is possible to access to the extremities of the edge with the property
    `extremities`, or specifically to the input node and the output node with the properties `input_node` and
    `output_node`. In addition, given one of the two extremities, it is possible to retrieve the other with the method
    `neighbor`. Finally the property `directed` can be used if it is not known if this link is an edge or an arc. In
    this case, it always returns True.
    """

    @property
    def extremities(self):
        """Return the two extremities of the arc.

        Return, in that order, the input node and the output node of the arc.
        """
        return super().extremities

    def neighbor(self, v):
        """Return the extremity of the arc not equal to v or None if v is not an extremity.

        :param v: an extremity of the arc
        :return: the extremity not equal to v or None if v is not an extremity.
        """
        return super().neighbor(v)

    @property
    def directed(self):
        """Return True. Use this method if it is not clear that this object is an edge or an arc. Equivalent to
        `isinstance(self, Arc)`"""
        return True

    @property
    def input_node(self):
        """Return the input node (or origin) of the arc."""
        return self._u

    @property
    def output_node(self):
        """Return the output node (or destination) of the arc."""
        return self._v

    def __str__(self):
        return str(self._u) + '->' + str(self._v)

    def __repr__(self):
        return str(self)
