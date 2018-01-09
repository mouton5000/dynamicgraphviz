"""Provide useful and simple classes to manage graphs.

Provide useful and simple classes to manage graphs. It contains the three internal classes
`_Graph`, `_Node`, `_Link`. Those three classes are superclasses of the undirected and directed
graph classes of the `undirectedgraph` and `directedgraph` packages.
"""


from pubsub import pub
from dynamicgraphviz.exceptions.graph_errors import *

__author__ = "Dimitri Watel"
__copyright__ = "Copyright 2018, dynamicgraphviz"


class _Graph:
    """Undirected and directed graphs.

    This class represents undirected and directed graphs (sets of vertices (or nodes) connected by edges or arcs,
    see https://en.wikipedia.org/wiki/Graph_theory for basic definitions).

    This class should not be instantiated. Use the class UndirectedGraph to build an undirected graph and the
    class DirectedGraph to build a directed graph. Those classes contains one property `nodes` to access to the nodes
    of the graph and two methods to simply edit them: `add_node` and `remove_node`. The class UndirectedGraph contains
    two properties `UndictedGraph.edges` and `UndictedGraph.nb_edges` to access to the edges and the number of edges of
    the graph and two methods to edit the edges: `UndirectedGraph.add_edge` and `UndictedGraph.remove_edge`. Similarly,
    the class DirectedGraph contains two properties `DirectedGraph.arcs` and `DirectedGraph.nb_arcs` and two methods
    `DirectedGraph.add_arc` and `DirectedGraph.remove_arc`. Finally, the three classes have the property `directed` to
    know whether the graph is directed or not, and the properties `links` and `nb_links` to directly access to the
    edges/arcs without knowing if the graph is directed.

    The graphs are simple :
    - if the graph is undirected, there are no two edges between the same two nodes and there is no loop.
    - if the graph is directed, there are no two arcs with the same input and output nodes and there is no loop. However
    there may be an arc from a node u to a node v and conversely an arc from v to u.

    For a graph g, it is possible to use
    - len(g) to get the number of node of g
    - str(g) to get a printable representation of the graph
    - iter(g) to get an iterator over the nodes of g (or 'for node in g:')
    - 'elem in g' to know if a node, an edge or an arc named elem is in g.

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
    def nb_links(self):
        """Return the number of links of the graph."""
        return len(self.__links)

    def _contain_node(self, node):
        return node in self.__nodes

    def _contain_link(self, link):
        return link in self.__links

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

    def add_node(self):
        """Add a new node to the graph and return it.

        Add a new node to the graph.
        :return the new added node.
        """
        node = self._build_node()
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
                raise NodeMembershipError(self, u)
            else:
                raise TypeError()

        if v not in self:
            if isinstance(v, _Node):
                raise NodeMembershipError(self, v)
            else:
                raise TypeError()

        if u == v:
            raise GraphError(self, 'A node cannot be linked to itself.')

        if self.directed and u.is_input_neighbor_of(v):
            raise LinkError(self, u.get_output_arc(v), 'The arc already exists.')

        if not self.directed and u.is_neighbor_of(v):
            raise LinkError(self, u.get_incident_edge(v), 'The edge already exists.')

        link, met = self._build_link(u, v)
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
            if self.directed:
                u._remove_incident_arc(l)
                v._remove_incident_arc(l)
            else:
                u._remove_incident_edge(l)
                v._remove_incident_edge(l)

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
