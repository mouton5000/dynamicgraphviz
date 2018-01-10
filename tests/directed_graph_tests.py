import unittest
from dynamicgraphviz.graph.directedgraph import DirectedGraph, DirectedNode, Arc
from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph
from dynamicgraphviz.exceptions.graph_errors import GraphError, LinkError, NodeMembershipError, LinkMembershipError
from pubsub import pub

CONCURRENTTEST = False
try:
    from concurrencytest import ConcurrentTestSuite, fork_for_tests
    CONCURRENTTEST = True
except ImportError:
    pass


class TestDirectedGraph(unittest.TestCase):

    def setUp(self):
        self.g = DirectedGraph()
        self.b = False
        self.currentnode = None
        self.currentarc = None

        self.g2 = DirectedGraph()
        v1 = self.g2.add_node()
        v2 = self.g2.add_node()
        v3 = self.g2.add_node()
        v4 = self.g2.add_node()
        v5 = self.g2.add_node()
        v6 = self.g2.add_node()
        v7 = self.g2.add_node()
        v8 = self.g2.add_node()
        self.nodes = [v1, v2, v3, v4, v5, v6, v7, v8]

        e1 = self.g2.add_arc(v1, v5)
        e2 = self.g2.add_arc(v2, v6)
        e3 = self.g2.add_arc(v3, v7)
        e4 = self.g2.add_arc(v4, v8)
        e5 = self.g2.add_arc(v1, v2)
        e6 = self.g2.add_arc(v2, v3)
        e7 = self.g2.add_arc(v3, v4)
        e8 = self.g2.add_arc(v4, v1)
        self.arcs = [e1, e2, e3, e4, e5, e6, e7, e8]

    def test_directed_graph_is_directed(self):
        self.assertTrue(self.g.directed)

    # ADD NODE TESTS

    def test_add_node_create_directed_node(self):
        v1 = self.g.add_node()
        self.assertIsInstance(v1, DirectedNode)

    def test_add_node_increase_size_by_one(self):
        n = 100
        for i in range(n):
            self.g.add_node()
            self.assertEqual(len(self.g), i + 1)

    def test_add_node_add_the_node_to_nodes_in_that_order(self):
        nodes = [self.g.add_node() for _ in range(100)]
        nodes2 = list(self.g)

        self.assertEqual(nodes, nodes2)

        nodes3 = list(self.g.nodes)
        self.assertEqual(nodes, nodes3)

    def test_graph_contain_added_nodes(self):
        n = 100
        nodes = [self.g.add_node() for _ in range(n)]
        for node in nodes:
            self.assertIn(node, self.g)

    def test_add_node_do_not_increase_arcs(self):
        n = 100
        for _ in range(n):
            self.g.add_node()
            self.assertEqual(len(list(self.g.arcs)), 0)

    def test_add_node_submit_pubsub_msg(self):
        pub.subscribe(self.receive_msg_add_node, str(id(self.g)) + '.add_node')
        v1 = self.g.add_node()
        if not self.b:
            self.assertFalse(True)
        else:
            self.assertEqual(v1, self.currentnode)

    def receive_msg_add_node(self, node, draw):
        self.b = not self.b
        self.assertIsInstance(node, DirectedNode)
        self.assertTrue(draw)
        self.currentnode = node

    # ADD ARCS

    def test_add_arc_create_an_arc(self):
        v1 = self.g.add_node()
        v2 = self.g.add_node()
        e = self.g.add_arc(v1, v2)
        self.assertIsInstance(e, Arc)

    def test_add_arc_increase_size_of_arcs_by_one(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        i = 0

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                self.g.add_arc(u, v)
                self.assertEqual(len(list(self.g.arcs)), i + 1)
                self.assertEqual(self.g.nb_arcs, i + 1)
                self.assertEqual(self.g.nb_links, i + 1)
                i += 1

    def test_add_arc_do_not_increase_nodes(self):

        n = 100
        for _ in range(n):
            self.g.add_node()

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                self.g.add_arc(u, v)
                self.assertEqual(len(self.g), n)

    def test_graph_contain_added_arcs(self):
        for _ in range(100):
            self.g.add_node()

        arcs = []

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                arc = self.g.add_arc(u, v)
                arcs.append(arc)
                self.assertIn(arc, self.g)

        for arc in arcs:
            self.assertIn(arc, self.g)

    def test_graph_not_contain_added_arcs_of_other_graph(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                self.g.add_arc(u, v)

        g2 = DirectedGraph()
        for _ in range(n):
            g2.add_node()

        for u in g2:
            for v in g2:
                if u == v:
                    continue
                arc = g2.add_arc(u, v)
                self.assertNotIn(arc, self.g)

    def test_add_arc_add_the_arc_to_arcs_in_that_order(self):
        arcs = []
        n = 100
        for _ in range(n):
            self.g.add_node()

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                arcs.append(self.g.add_arc(u, v))

        arcs2 = list(self.g.arcs)

        self.assertEqual(arcs, arcs2)

    def test_add_arc_submit_pubsub_msg(self):
        pub.subscribe(self.receive_msg_add_arc, str(id(self.g)) + '.add_arc')
        v1 = self.g.add_node()
        v2 = self.g.add_node()
        e = self.g.add_arc(v1, v2)
        if not self.b:
            self.assertFalse(True)
        else:
            self.assertEqual(e, self.currentarc)

    def receive_msg_add_arc(self, arc, draw):
        self.b = not self.b
        self.assertIsInstance(arc, Arc)
        self.assertTrue(draw)
        self.currentarc = arc

    def test_add_arc_raise_GraphError_with_same_nodes(self):
        v = self.g.add_node()
        with self.assertRaises(GraphError):
            self.g.add_arc(v, v)

    def test_add_arc_raise_TypeError_with_not_nodes(self):
        v = self.g.add_node()
        with self.assertRaises(TypeError):
            self.g.add_arc(1, v)
        with self.assertRaises(TypeError):
            self.g.add_arc('abc', 2.0)
        with self.assertRaises(TypeError):
            self.g.add_arc(1, 1)
        with self.assertRaises(TypeError):
            self.g.add_arc(v, 'abc')

    def test_add_arc_raise_NodeMembershipError_with_uncontained_nodes(self):
        v = self.g.add_node()
        g2 = DirectedGraph()
        w1 = g2.add_node()
        g3 = UndirectedGraph()
        w2 = g3.add_node()
        with self.assertRaises(NodeMembershipError):
            self.g.add_arc(v, w1)
        with self.assertRaises(NodeMembershipError):
            self.g.add_arc(v, w2)
        with self.assertRaises(NodeMembershipError):
            self.g.add_arc(w1, w2)

    def test_add_arc_raise_LinkError_if_arc_exists(self):
        v1 = self.g.add_node()
        v2 = self.g.add_node()
        self.g.add_arc(v1, v2)
        with self.assertRaises(LinkError):
            self.g.add_arc(v1, v2)
        try:
            self.g.add_arc(v2, v1)
        except LinkError:
            self.assertFalse(True)
        with self.assertRaises(LinkError):
            self.g.add_arc(v1, v2)

    # REMOVE ARC

    def test_remove_arc_decrease_size_of_arcs_by_one(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        arcs = []
        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                e = self.g.add_arc(u, v)
                arcs.append(e)

        for i, e in enumerate(arcs):
            self.g.remove_arc(e)
            self.assertEqual(len(list(self.g.arcs)), (n*(n-1)) - 1 - i)
            self.assertEqual(self.g.nb_arcs, (n*(n-1)) - 1 - i)
            self.assertEqual(self.g.nb_links, (n*(n-1)) - 1 - i)

    def test_remove_arc_do_not_decrease_nodes(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        arcs = []
        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                e = self.g.add_arc(u, v)
                arcs.append(e)

        for i, e in enumerate(arcs):
            self.g.remove_arc(e)
            self.assertEqual(len(self.g), n)

    def test_graph_not_contain_removed_arcs(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        arcs = []
        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                a = self.g.add_arc(u, v)
                arcs.append(a)

        for i, a in enumerate(arcs):
            self.g.remove_arc(a)
            self.assertNotIn(a, self.g)

        # Try after all removal
        for a in arcs:
            self.assertNotIn(a, self.g)

    def test_remove_arc_u_v_does_not_remove_v_u(self):
        u = self.g.add_node()
        v = self.g.add_node()

        e = self.g.add_arc(u, v)
        f = self.g.add_arc(v, u)

        self.g.remove_arc(e)

        self.assertIn(f, self.g)

    def test_remove_arc_remove_the_arc_from_arcs_in_that_order(self):
        arcs = []
        n = 100
        for _ in range(n):
            self.g.add_node()

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                arcs.append(self.g.add_arc(u, v))

        import random
        random.seed(100)
        while len(arcs) > 0:
            arc = random.choice(arcs)
            arcs.remove(arc)
            self.g.remove_arc(arc)
            self.assertEqual(arcs, list(self.g.arcs))

        self.assertEqual(arcs, list(self.g.arcs))

    def test_remove_arc_submit_pubsub_msg(self):
        pub.subscribe(self.receive_msg_remove_arc, str(id(self.g)) + '.remove_arc')
        u = self.g.add_node()
        v = self.g.add_node()
        e = self.g.add_arc(u, v)
        self.g.remove_arc(e)
        if not self.b:
            self.assertFalse(True)
        else:
            self.assertEqual(e, self.currentarc)

    def receive_msg_remove_arc(self, arc, draw):
        self.b = not self.b
        self.assertIsInstance(arc, Arc)
        self.assertTrue(draw)
        self.currentarc = arc

    def test_remove_arc_raise_TypeError_with_not_arc(self):
        u = self.g.add_node()
        v = self.g.add_node()
        self.g.add_arc(u, v)

        with self.assertRaises(TypeError):
            self.g.remove_arc(1)

        with self.assertRaises(TypeError):
            self.g.remove_arc('abc')

        with self.assertRaises(TypeError):
            self.g.remove_arc((u, v))

        with self.assertRaises(TypeError):
            self.g.remove_arc(u)

        with self.assertRaises(TypeError):
            self.g.remove_arc(None)

    def test_remove_arc_raise_LinkMembershipError_with_not_contained_arc(self):
        v1 = self.g.add_node()
        v2 = self.g.add_node()
        self.g.add_arc(v1, v2)

        g2 = DirectedGraph()
        v3 = g2.add_node()
        v4 = g2.add_node()
        e2 = g2.add_arc(v3, v4)

        g3 = UndirectedGraph()
        v5 = g3.add_node()
        v6 = g3.add_node()
        e3 = g3.add_edge(v5, v6)

        with self.assertRaises(LinkMembershipError):
            self.g.remove_arc(e2)

        with self.assertRaises(LinkMembershipError):
            self.g.remove_arc(e3)

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

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                self.g.add_arc(u, v)

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

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                self.g.add_arc(u, v)

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
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                self.g.add_arc(u, v)

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

    def test_remove_node_decreases_nb_arcs(self):
        self.g2.remove_node(self.nodes[2])

        self.assertEqual(len(list(self.g2.arcs)), 5)
        self.assertEqual(self.g2.nb_arcs, 5)
        self.assertEqual(self.g2.nb_links, 5)

    def test_remove_node_do_remove_incident_arcs_2(self):
        n = 100
        for _ in range(n):
            self.g.add_node()

        nodes = list(self.g)

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
                self.g.add_arc(u, v)

        import random
        random.seed(100)

        for v in nodes:
            self.g.remove_node(v)

        self.assertEqual(self.g.nb_arcs, 0)
        self.assertEqual(self.g.nb_links, 0)
        self.assertEqual(list(self.g.arcs), [])

    def test_remove_node_do_remove_incident_arcs(self):
        self.g2.remove_node(self.nodes[2])
        indexes = [2, 5, 6]
        for i in range(8):
            if i in indexes:
                self.assertNotIn(self.arcs[i], self.g2)
            else:
                self.assertIn(self.arcs[i], self.g2)

    def test_remove_node_u_remove_edge_u_v_and_v_u(self):
        u = self.g.add_node()
        v = self.g.add_node()

        e = self.g.add_arc(u, v)
        f = self.g.add_arc(v, u)

        self.g.remove_node(u)
        self.assertNotIn(e, self.g)
        self.assertNotIn(f, self.g)

    def test_remove_node_submit_pubsub_msg(self):
        pub.subscribe(self.receive_msg_remove_node, str(id(self.g)) + '.remove_node')
        u = self.g.add_node()
        v = self.g.add_node()
        self.g.add_arc(u, v)
        self.g.remove_node(u)

        self.assertTrue(self.b)
        self.assertEqual(u, self.currentnode)

    def receive_msg_remove_node(self, node, draw):
        self.b = not self.b
        self.assertIsInstance(node, DirectedNode)
        self.assertTrue(draw)
        self.currentnode = node

    def test_remove_node_submit_pubsub_remove_edge_msg(self):
        pub.subscribe(self.receive_msg_remove_arc_from_remove_node, str(id(self.g2)) + '.remove_arc')

        self.g2.remove_node(self.nodes[4])
        self.assertTrue(self.b)
        self.assertEqual(self.arcs[0], self.currentarc)

    def receive_msg_remove_arc_from_remove_node(self, arc, draw):
        self.b = not self.b
        self.assertIsInstance(arc, Arc)
        self.assertFalse(draw)  # !!
        self.currentarc = arc

    def test_remove_node_raise_TypeError_with_not_node(self):
        u = self.g.add_node()
        v = self.g.add_node()
        a = self.g.add_arc(u, v)

        with self.assertRaises(TypeError):
            self.g.remove_node(1)

        with self.assertRaises(TypeError):
            self.g.remove_node('abc')

        with self.assertRaises(TypeError):
            self.g.remove_node((u, v))

        with self.assertRaises(TypeError):
            self.g.remove_node(None)

        with self.assertRaises(TypeError):
            self.g.remove_node(a)

    def test_remove_node_raise_NodeMembershipError_with_not_contained_node(self):
        u = self.g.add_node()
        v = self.g.add_node()
        self.g.add_arc(u, v)

        g2 = DirectedGraph()
        v3 = g2.add_node()
        v4 = g2.add_node()
        g2.add_arc(v3, v4)

        g3 = UndirectedGraph()
        v5 = g3.add_node()
        v6 = g3.add_node()
        g3.add_edge(v5, v6)

        with self.assertRaises(NodeMembershipError):
            self.g.remove_node(v3)

        with self.assertRaises(NodeMembershipError):
            self.g.remove_node(v5)


if __name__ == '__main__':

    if CONCURRENTTEST:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestDirectedGraph)
        runner = unittest.TextTestRunner()
        concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests(50))
        runner.run(concurrent_suite)
    else:
        unittest.main()
