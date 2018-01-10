import unittest

from dynamicgraphviz.graph.directedgraph import DirectedGraph
from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph, UndirectedNode, Edge
from dynamicgraphviz.exceptions.graph_errors import GraphError, NodeMembershipError, LinkError, LinkMembershipError
from pubsub import pub

CONCURRENTTEST = False
try:
    from concurrencytest import ConcurrentTestSuite, fork_for_tests
    CONCURRENTTEST = True
except ImportError:
    pass


class TestUndirectedGraph(unittest.TestCase):

    def setUp(self):
        self.g = UndirectedGraph()
        self.b = False
        self.currentnode = None
        self.currentedge = None

        self.g2 = UndirectedGraph()
        v1 = self.g2.add_node()
        v2 = self.g2.add_node()
        v3 = self.g2.add_node()
        v4 = self.g2.add_node()
        v5 = self.g2.add_node()
        v6 = self.g2.add_node()
        v7 = self.g2.add_node()
        v8 = self.g2.add_node()
        self.nodes = [v1, v2, v3, v4, v5, v6, v7, v8]

        e1 = self.g2.add_edge(v1, v5)
        e2 = self.g2.add_edge(v2, v6)
        e3 = self.g2.add_edge(v3, v7)
        e4 = self.g2.add_edge(v4, v8)
        e5 = self.g2.add_edge(v1, v2)
        e6 = self.g2.add_edge(v2, v3)
        e7 = self.g2.add_edge(v3, v4)
        e8 = self.g2.add_edge(v4, v1)
        self.edges = [e1, e2, e3, e4, e5, e6, e7, e8]

    def test_undirected_graph_is_undirected(self):
        self.assertFalse(self.g.directed)

    # ADD NODE TESTS

    def test_add_node_create_undirected_node(self):
        v1 = self.g.add_node()
        self.assertIsInstance(v1, UndirectedNode)

    def test_add_node_increase_size_by_one(self):
        n = 100
        for i in range(n):
            self.g.add_node()
            self.assertEqual(len(self.g), i + 1)
            self.assertEqual(len(list(self.g.nodes)), i + 1)

    def test_add_node_add_the_node_to_nodes_in_that_order(self):
        n = 100
        nodes = [self.g.add_node() for _ in range(n)]
        nodes2 = list(self.g)

        self.assertEqual(nodes, nodes2)

        nodes3 = list(self.g.nodes)
        self.assertEqual(nodes, nodes3)

    def test_graph_contain_added_nodes(self):
        n = 100
        nodes = [self.g.add_node() for _ in range(n)]
        for node in nodes:
            self.assertIn(node, self.g)

    def test_add_node_do_not_increase_edges(self):
        n = 100
        for _ in range(n):
            self.g.add_node()
            self.assertEqual(len(list(self.g.edges)), 0)

    def test_add_node_submit_pubsub_msg(self):
        pub.subscribe(self.receive_msg_add_node, str(id(self.g)) + '.add_node')
        v1 = self.g.add_node()
        self.assertTrue(self.b)
        self.assertEqual(v1, self.currentnode)

    def receive_msg_add_node(self, node, draw):
        self.b = not self.b
        self.assertIsInstance(node, UndirectedNode)
        self.assertTrue(draw)
        self.currentnode = node

    # ADD EDGES

    def test_add_edge_create_an_edge(self):
        v1 = self.g.add_node()
        v2 = self.g.add_node()
        e = self.g.add_edge(v1, v2)
        self.assertIsInstance(e, Edge)

    def test_add_edge_increase_size_of_edges_by_one(self):

        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        for i, couple in enumerate(couples):
            u, v = couple
            self.g.add_edge(u, v)
            self.assertEqual(len(list(self.g.edges)), i + 1)
            self.assertEqual(self.g.nb_edges, i + 1)
            self.assertEqual(self.g.nb_links, i + 1)

    def test_add_edge_do_not_increase_nodes(self):

        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        for i, couple in enumerate(couples):
            u, v = couple
            self.g.add_edge(u, v)
            self.assertEqual(len(self.g), n)

    def test_graph_contain_added_edges(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        edges = []

        for u, v in couples:
            edge = self.g.add_edge(u, v)
            edges.append(edge)
            self.assertIn(edge, self.g)

        for edge in edges:
            self.assertIn(edge, self.g)

    def test_graph_not_contain_added_edges_of_other_graph(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        for u, v in couples:
            self.g.add_edge(u, v)

        g2 = UndirectedGraph()
        for _ in range(n):
            g2.add_node()

        nodes = list(g2)
        import itertools
        couples = itertools.combinations(nodes, 2)

        for u, v in couples:
            edge = g2.add_edge(u, v)
            self.assertNotIn(edge, self.g)

    def test_add_edge_add_the_edge_to_edges_in_that_order(self):
        edges = []
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        for u, v in couples:
            edges.append(self.g.add_edge(u, v))

        edges2 = list(self.g.edges)

        self.assertEqual(edges, edges2)

    def test_add_edge_submit_pubsub_msg(self):
        pub.subscribe(self.receive_msg_add_edge, str(id(self.g)) + '.add_arc')
        v1 = self.g.add_node()
        v2 = self.g.add_node()
        e = self.g.add_edge(v1, v2)
        self.assertTrue(self.b)
        self.assertEqual(e, self.currentedge)

    def receive_msg_add_edge(self, arc, draw):
        self.b = not self.b
        self.assertIsInstance(arc, Edge)
        self.assertTrue(draw)
        self.currentedge = arc

    def test_add_edge_raise_GraphError_with_same_nodes(self):
        v = self.g.add_node()
        with self.assertRaises(GraphError):
            self.g.add_edge(v, v)

    def test_add_edge_raise_TypeError_with_not_nodes(self):
        v = self.g.add_node()
        with self.assertRaises(TypeError):
            self.g.add_edge(1, v)
        with self.assertRaises(TypeError):
            self.g.add_edge('abc', 2.0)
        with self.assertRaises(TypeError):
            self.g.add_edge(1, 1)
        with self.assertRaises(TypeError):
            self.g.add_edge(v, 'abc')

    def test_add_edge_raise_NodeMembershipError_with_not_contained_nodes(self):
        v = self.g.add_node()
        g2 = UndirectedGraph()
        w1 = g2.add_node()
        g3 = DirectedGraph()
        w2 = g3.add_node()
        with self.assertRaises(NodeMembershipError):
            self.g.add_edge(v, w1)
        with self.assertRaises(NodeMembershipError):
            self.g.add_edge(v, w2)
        with self.assertRaises(NodeMembershipError):
            self.g.add_edge(w1, w2)

    def test_add_edge_raise_LinkError_if_edge_exists(self):
        v1 = self.g.add_node()
        v2 = self.g.add_node()
        self.g.add_edge(v1, v2)
        with self.assertRaises(LinkError):
            self.g.add_edge(v1, v2)
        with self.assertRaises(LinkError):
            self.g.add_edge(v2, v1)

    # REMOVE EDGE

    def test_remove_edge_decrease_size_of_edges_by_one(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        edges = []
        for u, v in couples:
            e = self.g.add_edge(u, v)
            edges.append(e)

        for i, e in enumerate(edges):
            self.g.remove_edge(e)
            self.assertEqual(len(list(self.g.edges)), (n*(n-1)) // 2 - 1 - i)
            self.assertEqual(self.g.nb_edges, (n*(n-1)) // 2 - 1 - i)
            self.assertEqual(self.g.nb_links, (n*(n-1)) // 2 - 1 - i)

    def test_remove_edge_do_not_decrease_nodes(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        edges = []
        for u, v in couples:
            e = self.g.add_edge(u, v)
            edges.append(e)

        for i, e in enumerate(edges):
            self.g.remove_edge(e)
            self.assertEqual(len(self.g), n)

    def test_graph_not_contain_removed_edges(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        edges = []
        for u, v in couples:
            e = self.g.add_edge(u, v)
            edges.append(e)

        for i, e in enumerate(edges):
            self.g.remove_edge(e)
            self.assertNotIn(e, self.g)

        # Try after all removal
        for e in edges:
            self.assertNotIn(e, self.g)

    def test_remove_edge_remove_the_edge_from_edges_in_that_order(self):
        edges = []
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        for u, v in couples:
            edges.append(self.g.add_edge(u, v))

        import random
        random.seed(100)
        while len(edges) > 0:
            edge = random.choice(edges)
            edges.remove(edge)
            self.g.remove_edge(edge)
            self.assertEqual(edges, list(self.g.edges))

        self.assertEqual(edges, list(self.g.edges))

    def test_remove_edge_submit_pubsub_msg(self):
        pub.subscribe(self.receive_msg_remove_edge, str(id(self.g)) + '.remove_arc')
        u = self.g.add_node()
        v = self.g.add_node()
        e = self.g.add_edge(u, v)
        self.g.remove_edge(e)
        self.assertTrue(self.b)
        self.assertEqual(e, self.currentedge)

    def receive_msg_remove_edge(self, arc, draw):
        self.b = not self.b
        self.assertIsInstance(arc, Edge)
        self.assertTrue(draw)
        self.currentedge = arc

    def test_remove_edge_raise_TypeError_with_not_edge(self):
        u = self.g.add_node()
        v = self.g.add_node()
        self.g.add_edge(u, v)

        with self.assertRaises(TypeError):
            self.g.remove_edge(1)

        with self.assertRaises(TypeError):
            self.g.remove_edge('abc')

        with self.assertRaises(TypeError):
            self.g.remove_edge((u, v))

        with self.assertRaises(TypeError):
            self.g.remove_edge(u)

        with self.assertRaises(TypeError):
            self.g.remove_edge(None)

    def test_remove_edge_raise_LinkMembershipError_with_not_contained_edge(self):
        u = self.g.add_node()
        v = self.g.add_node()
        self.g.add_edge(u, v)

        g2 = UndirectedGraph()
        v3 = g2.add_node()
        v4 = g2.add_node()
        e2 = g2.add_edge(v3, v4)

        g3 = DirectedGraph()
        v5 = g3.add_node()
        v6 = g3.add_node()
        e3 = g3.add_arc(v5, v6)

        with self.assertRaises(LinkMembershipError):
            self.g.remove_edge(e2)

        with self.assertRaises(LinkMembershipError):
            self.g.remove_edge(e3)

    # REMOVE NODE

    def test_remove_node_decrease_size_of_nodes_by_one_empty_graph(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        for i, v in enumerate(nodes):
            self.g.remove_node(v)
            self.assertEqual(len(self.g), n - i - 1)
            self.assertEqual(len(list(self.g.nodes)), n - i - 1)

    def test_remove_node_decrease_size_of_nodes_by_one_not_empty_graph(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        for u, v in couples:
            self.g.add_edge(u, v)

        for i, v in enumerate(nodes):
            self.g.remove_node(v)
            self.assertEqual(len(self.g), n - i - 1)
            self.assertEqual(len(list(self.g.nodes)), n - i - 1)

    def test_graph_not_contain_removed_nodes_empty_graph(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        for v in nodes:
            self.g.remove_node(v)
            self.assertNotIn(v, self.g)

        # After removal
        for v in nodes:
            self.assertNotIn(v, self.g)

    def test_graph_not_contain_removed_nodes_not_empty_graph(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        for u, v in couples:
            self.g.add_edge(u, v)

        for v in nodes:
            self.g.remove_node(v)
            self.assertNotIn(v, self.g)

        # After removal
        for v in nodes:
            self.assertNotIn(v, self.g)

    def test_remove_node_remove_the_node_from_nodes_in_that_order_empty_graph(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import random
        random.seed(100)

        while len(nodes) > 0:
            v = random.choice(nodes)
            nodes.remove(v)
            self.g.remove_node(v)
            self.assertEqual(nodes, list(self.g.nodes))
            self.assertEqual(nodes, list(self.g))

        self.assertEqual(nodes, list(self.g.nodes))
        self.assertEqual(nodes, list(self.g))

    def test_remove_node_remove_the_node_from_nodes_in_that_order_not_empty_graph(self):
        edges = []
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        for u, v in couples:
            edges.append(self.g.add_edge(u, v))

        import random
        random.seed(100)

        while len(nodes) > 0:
            v = random.choice(nodes)
            nodes.remove(v)
            self.g.remove_node(v)
            self.assertEqual(nodes, list(self.g.nodes))
            self.assertEqual(nodes, list(self.g))

        self.assertEqual(nodes, list(self.g.nodes))
        self.assertEqual(nodes, list(self.g))

    def test_remove_node_decreases_nb_edges(self):
        self.g2.remove_node(self.nodes[2])

        self.assertEqual(len(list(self.g2.edges)), 5)
        self.assertEqual(self.g2.nb_edges, 5)
        self.assertEqual(self.g2.nb_links, 5)

    def test_remove_node_do_remove_incident_edges_2(self):
        edges = []
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)
        import itertools
        couples = itertools.combinations(nodes, 2)

        for u, v in couples:
            edges.append(self.g.add_edge(u, v))

        import random
        random.seed(100)

        for v in nodes:
            self.g.remove_node(v)

        self.assertEqual(self.g.nb_edges, 0)
        self.assertEqual(self.g.nb_links, 0)
        self.assertEqual(list(self.g.edges), [])

    def test_remove_node_do_remove_incident_edges(self):
        self.g2.remove_node(self.nodes[2])
        indexes = [2, 5, 6]
        for i in range(8):
            if i in indexes:
                self.assertNotIn(self.edges[i], self.g2)
            else:
                self.assertIn(self.edges[i], self.g2)

    def test_remove_node_submit_pubsub_msg(self):
        pub.subscribe(self.receive_msg_remove_node, str(id(self.g)) + '.remove_node')
        u = self.g.add_node()
        v = self.g.add_node()
        self.g.add_edge(u, v)
        self.g.remove_node(u)

        self.assertTrue(self.b)
        self.assertEqual(u, self.currentnode)

    def receive_msg_remove_node(self, node, draw):
        self.b = not self.b
        self.assertIsInstance(node, UndirectedNode)
        self.assertTrue(draw)
        self.currentnode = node

    def test_remove_node_submit_pubsub_remove_edge_msg(self):
        pub.subscribe(self.receive_msg_remove_edge_from_remove_node, str(id(self.g2)) + '.remove_arc')

        self.g2.remove_node(self.nodes[4])
        self.assertTrue(self.b)
        self.assertEqual(self.edges[0], self.currentedge)

    def receive_msg_remove_edge_from_remove_node(self, arc, draw):
        self.b = not self.b
        self.assertIsInstance(arc, Edge)
        self.assertFalse(draw)  # !!
        self.currentedge = arc

    def test_remove_node_raise_TypeError_with_not_node(self):
        u = self.g.add_node()
        v = self.g.add_node()
        e = self.g.add_edge(u, v)

        with self.assertRaises(TypeError):
            self.g.remove_node(1)

        with self.assertRaises(TypeError):
            self.g.remove_node('abc')

        with self.assertRaises(TypeError):
            self.g.remove_node((u, v))

        with self.assertRaises(TypeError):
            self.g.remove_node(None)

        with self.assertRaises(TypeError):
            self.g.remove_node(e)

    def test_remove_node_raise_NodeMembershipError_with_not_contained_node(self):
        u = self.g.add_node()
        v = self.g.add_node()
        self.g.add_edge(u, v)

        g2 = UndirectedGraph()
        v3 = g2.add_node()
        v4 = g2.add_node()
        g2.add_edge(v3, v4)

        g3 = DirectedGraph()
        v5 = g3.add_node()
        v6 = g3.add_node()
        g3.add_arc(v5, v6)

        with self.assertRaises(NodeMembershipError):
            self.g.remove_node(v3)

        with self.assertRaises(NodeMembershipError):
            self.g.remove_node(v5)


if __name__ == '__main__':

    if CONCURRENTTEST:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestUndirectedGraph)
        runner = unittest.TextTestRunner()
        concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests(50))
        runner.run(concurrent_suite)
    else:
        unittest.main()
