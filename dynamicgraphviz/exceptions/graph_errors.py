"""Define all the graph exceptions that can occurs while using the module `graph`.

There are two categories of exceptions: the `NodeError`, the `LinkError`. The specific `NodeMembershipError` and
`LinkMembershipError` are subclasses of those two classes and are raised when the user try to manage a node, an edge
or an arc with a graph to which they do not belong.

All those exceptions are subclasses of the general class `GraphError`.
"""


class GraphError(Exception):
    """Error raised when working with graphs."""
    def __init__(self, g, msg):
        """Define a Graph error about the graph g described with the message msg."""
        self.graph = g
        self.message = 'Graph ' + repr(self.graph) + ' error: ' + msg


class NodeError(GraphError):
    """Error raised when working with nodes."""
    def __init__(self, g, v, msg):
        """Define a Node error about the graph g and the node v described with the message msg."""
        super().__init__(g, '')
        self.node = v
        self.message = 'Node ' + str(v) + ' in graph ' + repr(self.graph) + ' error: ' + msg


class NodeMembershipError(NodeError):
    """Error raised when a node is supposed to belong to a graph but is not."""
    def __init__(self, g, v):
        """Define a Node membership error about the graph g and the node v."""
        super().__init__(g, v, 'The node does not belong to the graph.')


class LinkError(GraphError):
    """Error raised when working with edges or arcs."""
    def __init__(self, g, l, msg):
        """Define a Link error about the graph g and the edge or arc l described with the message msg."""
        super().__init__(g, '')
        self.link = l
        self.message = ('Arc ' if l.directed else 'Edge ') + str(l) + ' in graph ' + repr(self.graph) + ' error: ' + msg


class LinkMembershipError(LinkError):
    """Error raised when a link is supposed to belong to a graph but is not."""
    def __init__(self, g, l):
        """Define a Link membership error about the graph g and the link l."""
        super().__init__(g, l, 'The ' + ('arc' if l.directed else 'edge') + ' does not belong to the graph.')
