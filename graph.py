"""Provide useful and simple classes to manage Directed and Undirected graphs.

Provide useful and simple classes to manage Directed and Undirected graphs. It contains the six classes
`UndirectedGraph`, `UndirectedNode`, `Edge`, `DirectedGraph`, `DirectedNode` and `Arc`.

The reason why there are six classes instead of three modeling at the same time the Undirected and the directed case is
only a mater of vocabulary. We talk about edges and neighbors in the undirected case, and we talk about arcs, input
arcs, output arcs, input neighbor, ... in the directed case. Thus, the directed classes are mostly the same as the
undirected ones where every method or property is tripled. The good point is that the name of the methods are consistent
with the used case (directed or undirected).

To build a graph, use the graph classes. It is not recommended to manually instantiate a node, an edge or an arc as it
is not possible to link them with the graph objects. The graph classes have methods to manage the nodes and the link
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

from pubsub import pub
from itertools import chain
from exceptions.graph_errors import *


class _Graph:
    """Undirected and directed graphs.

    This class represents undirected and directed graphs (sets of vertices (or nodes) connected by edges or arcs,
    see https://en.wikipedia.org/wiki/Graph_theory for basic definitions).

    This class should not be instantiated. Use the class UndirectedGraph to build an undirected graph and the
    class DirectedGraph to build a directed graph. Those classes contains one property `nodes` to access to the nodes
    of the graph and two methods to simply edit them: `add_node` and `remove_node`. The class UndirectedGraph contains
    one property `UndictedGraph.edges` to access to the edges of the graph and two methods to edit the edges:
    `UndirectedGraph.add_edge` and `UndictedGraph.remove_edge`. Similarly, the class DirectedGraph contains one
    property `DirectedGraph.arcs` and two methods `DirectedGraph.add_arc` and `DirectedGraph.remove_arc`. Finally,
    the three classes have the property `directed` to know whether the graph is directed or not.

    The graph are simple :
    - if the graph is undirected, there are no two edges between the same two nodes and there is no loop.
    - if the graph is directed, there are no two arcs with the same input and output nodes and there is no loop. However
    there may be an arc from a node u to a node v and conversely an arc from v to u.

    For a graph g, it is possible to use
    - len(g) to get the number of node of g
    - str(g) to get a printable representation of the graph
    - iter(g) to get an iterator over the nodes of g (or 'for node in g:')
    - 'node in g' to know if a node is in g.

    WARNING : The graph should be edited only with the methods `add_node`, `remove_node, `UndirectedGraph.add_edge`,
    `UndictedGraph.remove_edge`, `DirectedGraph.add_arc` and `DirectedGraph.remove_arc` otherwise an unexpected
    behaviour may occurs.
    """

    def __init__(self, directed=False):
        """ Build an empty graph.

        Build a new graph with no node (and thus no edge or arc).
        :param directed: Determine whether the graph is directed or not.
        """
        self.__nodes = []
        self.__links = []
        self.__directed = directed

    def __len__(self):
        """Return the number of nodes of the graph."""
        return len(self.__nodes)

    @property
    def nodes(self):
        """Return an iterator through the list of nodes of the graph. This functions is identical to iter(self). """
        return iter(self.__nodes)

    @property
    def links(self):
        """Return an iterator through the list of edges or arcs of the graph.

        Return an iterator through the list of edges or arcs of the graph. Use this function if you do not know
        whether the graph is directed or not. In you do, for readability, use the methods `UndirectedGraph.edges` and
        `DirectedGraph.arcs` instead."""
        return iter(self.__links)

    @property
    def directed(self):
        """Return True if the graph is directed and False otherwise."""
        return self.__directed

    def __iter__(self):
        """Return an iterator through the nodes of the graph. This function is identical to `self.nodes`."""
        return self.nodes

    def __contains__(self, node):
        """Return True if node is a node of the graph."""
        return node in self.__nodes

    def add_node(self):
        """Add a new node to the graph and return it.

        Add a new node to the graph.
        :return the new added node.
        """
        if self.directed:
            node = DirectedNode(self)
        else:
            node = UndirectedNode(self)
        self.__nodes.append(node)

        # Publish a message so that any listener is aware that a node was added
        pub.sendMessage(str(id(self)) + '.add_node', node=node, draw=True)
        return node

    def remove_node(self, v):
        """Remove the node v of the graph.

        Remove the node v of the graph. That node should belong to the graph, otherwise an exception is raised.
        Every incident edge or arc of that node is also removed.

        :param v: a node of the graph that should be removed.
        :raises TypeError: if v is not a node.
        :raises NodeMembershipError: if v does not belong to the graph.
        """
        try:
            self.__nodes.remove(v)
            for arc in list(v.incident_edges_and_arcs):
                # Remove the incident edges or arcs of the nodes. Any listener will be aware that those edges/arcs
                # are removed. If the listener draws the graphs, the False parameter tells it not to immediately update
                # the drawing, it will be done when the node is removed.
                self.__remove_link(arc, False)

            # Publish a message so that any listener is aware that a node was removed
            pub.sendMessage(str(id(self)) + '.remove_node', node=v, draw=True)
        except ValueError:
            if isinstance(v, _Node):
                raise NodeMembershipError(self, v)
            else:
                raise TypeError()

    def _add_link(self, u, v):
        """Add an edge or an arc to the graph and return it.

        If the graph is undirected, add an edge between the nodes u and v of the graph.
        If the graph is directed, add an arc from the node u to the node v of the graph.
        The nodes u and v should belong to the graph and not be equal, and there should not be already an edge between
        u and v is the graph is undirected, or an arc from u to v is the graph is directed, otherwise an exception is
        raised.

        :param u: a node of the graph
        :param v: a node of the graph, distinct from u
        :return: a new edge or arc linking u and v.
        :raises TypeError: if u or v is not a node
        :raises NodeMembershipError: if the node u or the node v does not belong to the graph
        :raises GraphError: if the node u equals the node v
        :raises LinkError: if the graph is undirected and if there is already an edge between u and v or if the graph is
        directed and there is already an arc from u to v.
        """
        if u not in self:
            if isinstance(u, _Node):
                raise TypeError()
            else:
                raise NodeMembershipError(self, u)

        if v not in self:
            if isinstance(v, _Node):
                raise TypeError()
            else:
                raise NodeMembershipError(self, v)

        if u == v:
            raise GraphError(self, 'A node cannot be linked to itself.')

        if self.directed and u.is_input_neighbor_of(v):
            raise LinkError(self, u.get_output_arc(v), 'The arc already exists.')

        if not self.directed and u.is_neighbor_of(v):
            raise LinkError(self, u.get_incident_edge(v), 'The edge already exists.')

        if not self.directed:
            cls = Edge
            met = UndirectedNode._add_incident_edge
        else:
            cls = Arc
            met = DirectedNode._add_incident_arc

        link = cls(u, v)
        met(u, link)
        met(v, link)
        self.__links.append(link)

        # Publish a message so that any listener is aware that an arc was added
        pub.sendMessage(str(id(self)) + '.add_arc', arc=link, draw=True)
        return link

    def __remove_link(self, l, draw=False):
        """Remove an edge or an arc of the graph.

        Remove the edge or arc l of the graph. That edge/arc should belong to the graph,
        otherwise an exception is raised.

        :param l: an edge or an arc of the graph that should be removed.
        :param draw: if True, immediately update the drawing of the graph
        :raises TypeError: if l is not an edge or an arc
        :raises LinkMembershipError: if the link l does not belong to the graph.
        """
        try:
            self.__links.remove(l)
            u, v = l.extremities
            u._remove_neighbor(v)
            v._remove_neighbor(u)

            # Publish a message so that any listener is aware that an arc was removed.
            # The draw parameters tells any drawer listener not to update the drawing.
            pub.sendMessage(str(id(self)) + '.remove_arc', arc=l, draw=draw)

        except ValueError:
            if isinstance(l, _Link):
                raise LinkMembershipError(self, l)
            else:
                raise TypeError()

    def _remove_link(self, l):
        """Remove an edge or an arc of the graph.

        Remove the edge or arc l of the graph. That edge/arc should belong to the graph,
        otherwise an exception is raised.

        :param l: an edge or an arc of the graph that should be removed.
        :raises TypeError: if l is not an edge or an arc
        :raises LinkMembershipError: if the link l does not belong to the graph.
        """
        return self.__remove_link(l, draw=True)

    def __str__(self):
        met = DirectedNode.is_output_neighbor_of if self.directed else UndirectedNode.is_neighbor_of
        return '\n'.join(' '.join([('1' if met(node2, node) else '0') for node2 in self]) for node in self)


class UndirectedGraph(_Graph):
    """Undirected graphs.

    This class represents undirected graphs (sets of vertices (or nodes) connected by edges,
    see https://en.wikipedia.org/wiki/Graph_theory for basic definitions). It contains four
    methods to simply edit the graph: `add_node`, `remove_node`, `add_edge` and `remove_edge` and two properties,
    `nodes` and `edges`, to respectively access to the nodes and the edges of the graph.

    The graph are simple: there are no two edges between the same two nodes and there is no loop.

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


class DirectedGraph(_Graph):
    """Directed graphs.

    This class represents directed graphs (sets of vertices (or nodes) connected by arcs,
    see https://en.wikipedia.org/wiki/Graph_theory for basic definitions). It contains four
    methods to simply edit the graph: `add_node`, `remove_node`, `add_arc` and `remove_arc` and two properties,
    `nodes`, `arcs` to respectively access to the nodes and the arcs of the graph.

    The graph are simple: there are no two arcs with the same input and output nodes and there is no loop. However
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


class _Node:
    """Vertice (or node) of an undirected or a directed graph.

    This class represents any node of an undirected or a directed graph. This class should not be manually
    instantiated. Use the methods `UndirectedGraph.add_node` or `DirectedGraph.add_node` instead. Otherwise unexpected
    behaviour may occurs.

    With the classes _Node, UndirectedNode and DirectedNode, it is possible to access to all the incident edges or arcs
    and to the corresponding neighbors. Moreover, a node has a unique index that can be used to easily identify that
    node and that is used when the node is printed with `str`.
    """

    _index = 1
    """Index of the next added node of the graph."""

    def __init__(self, g):
        """Build a new node of the graph g."""
        self.__graph = g
        self.__index = _Node._index
        _Node._index += 1

    @property
    def index(self):
        """Return the unique index of that node."""
        return self.__index

    def is_incident_to(self, l):
        """Return True if the node is incident to the link l (an edge if the graph is not directed and an arc
        otherwise) and False otherwise."""
        u, v = l.extremities
        return self == u or self == v

    def __str__(self):
        return str(self.__index)

    def __repr__(self):
        return str(self)


class UndirectedNode(_Node):
    """Vertice (or node) of an undirected graph.

    This class represents any node of an undirected graph. This class should not be manually instantiated. Use
    the method `UndirectedGraph.add_node` instead. Otherwise an unexpected behaviour may occurs.

    With this class, it is possible to access to all the incident edges and to the corresponding neighbors of the node.
    - the property `neighbors` and the method `is_neighbor_of` give access to the neighbors
    - the property `incident_edges` and the methods `get_incident_edge` and `is_incident_to` give access to the
    incident_edges

    Moreover, a node has a unique index that can be used to easily identify that node and that is used when the node
    is printed with `str`. That index is accessible with the property `index`.
    """

    def __init__(self, g):
        """Build a new node of the undirected graph g."""
        super().__init__(g)
        self.__edges = {}

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


class _Link:
    """Undirected edge or Directed arc.

    This class represents any edge of an undirected graph or any arc of a directed graph. This class should not be
    manually instantiated. Use the methods `UndirectedGraph.add_edge` or `DirectedGraph.add_arc` instead. Otherwise,
    an unexpected behaviour may occurs.

    With the classes _Link, Edge and Arc, it is possible to access to the extremities of the link with the property
    `extremities`. In addition, given one of the two extremities, it is possible to retrieve the other with the method
    `neighbor`. Finally use the property `directed` to know whether the link is an edge or an arc.
    """

    def __init__(self, u, v):
        """Build a new link between the node u and the node v

        :param u: a node of a graph
        :param v: a node of a same graph
        """
        self._u = u
        self._v = v

    @property
    def extremities(self):
        """Return the two extremities of the link."""
        return self._u, self._v

    def neighbor(self, v):
        """Return the extremity of the link not equal to v or None if v is not an extremity.

        :param v: an extremity of the link
        :return: the extremity not equal to v or None if v is not an extremity.
        """
        if v == self._u:
            return self._v
        elif v == self._v:
            return self._u
        return None

    def __str__(self):
        return str(self._u) + '--' + str(self._v)

    def __repr__(self):
        return str(self)


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


if __name__ == '__main__':
    g = DirectedGraph()

    v1 = g.add_node()
    v2 = g.add_node()
    v3 = g.add_node()
    v4 = g.add_node()

    a1 = g.add_arc(v1, v2)
    a2 = g.add_arc(v2, v3)
    a3 = g.add_arc(v3, v4)
    a4 = g.add_arc(v4, v1)

    print(g)

    from gui.graphDrawer import GraphDrawer
    gd = GraphDrawer(g)
    v5 = g.add_node()
    g.add_arc(v5, v1)
    gd.place_nodes(True)

    v6 = g.add_node()
    g.add_arc(v1, v6)
    g.add_arc(v3, v6)
    g.add_arc(v6, v5)
    gd.place_nodes(True)

    gd.set_node_radius(v1, 50, True)
    gd.set_line_width(v1, 0, True)

    gd.pause()

    import time
    time.sleep(1.5)
