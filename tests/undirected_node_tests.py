import unittest

from dynamicgraphviz.graph.directedgraph import DirectedGraph
from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph, UndirectedNode, Edge
from dynamicgraphviz.exceptions.graph_errors import GraphError, NodeMembershipError, LinkError, LinkMembershipError, \
    NodeError

CONCURRENTTEST = False
try:
    from concurrencytest import ConcurrentTestSuite, fork_for_tests
    CONCURRENTTEST = True
except ImportError:
    pass


class TestUndirectedNode(unittest.TestCase):

    def setUp(self):
        self.g = UndirectedGraph()
        v1 = self.g.add_node()
        v2 = self.g.add_node()
        v3 = self.g.add_node()
        v4 = self.g.add_node()
        v5 = self.g.add_node()
        v6 = self.g.add_node()
        v7 = self.g.add_node()
        v8 = self.g.add_node()
        self.nodes = [v1, v2, v3, v4, v5, v6, v7, v8]

        self.couples = [(v1, v5), (v2, v6), (v3, v7), (v4, v8), (v1, v2), (v2, v3), (v3, v4), (v4, v1)]
        self.edges = [self.g.add_edge(u, v) for u, v in self.couples]

    def test_add_node_increase_index(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.assertEqual(v1.index + 1, v2.index)
        self.assertEqual(v2.index + 1, v3.index)
        self.assertEqual(v3.index + 1, v4.index)
        self.assertEqual(v4.index + 1, v5.index)
        self.assertEqual(v5.index + 1, v6.index)
        self.assertEqual(v6.index + 1, v7.index)
        self.assertEqual(v7.index + 1, v8.index)

    def test_add_edge_increase_nb_neighbors(self):
        sizes = [3, 3, 3, 3, 1, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(len(v), size)
            self.assertEqual(v.nb_neighbors, size)

    def test_add_node_do_not_increase_nb_neighbors(self):
        self.g.add_node()
        self.g.add_node()
        self.g.add_node()

        sizes = [3, 3, 3, 3, 1, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(len(v), size)
            self.assertEqual(v.nb_neighbors, size)

    def test_remove_node_decrease_nb_neighbors_of_neighbors(self):
        self.g.remove_node(self.nodes[0])
        sizes = [2, 3, 2, 0, 1, 1, 1]

        for v, size in zip(self.nodes[1:], sizes):
            self.assertEqual(len(v), size)
            self.assertEqual(v.nb_neighbors, size)

        self.g.remove_node(self.nodes[5])
        sizes = [1, 3, 2, 0, 1, 1]

        for v, size in zip(self.nodes[1:5]+self.nodes[6:], sizes):
            self.assertEqual(len(v), size)
            self.assertEqual(v.nb_neighbors, size)

    def test_remove_edge_decrease_nb_neighbors_of_extremities(self):
        self.g.remove_edge(self.edges[0])
        sizes = [2, 3, 3, 3, 0, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(len(v), size)
            self.assertEqual(v.nb_neighbors, size)

        self.g.remove_edge(self.edges[4])
        sizes = [1, 2, 3, 3, 0, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(len(v), size)
            self.assertEqual(v.nb_neighbors, size)

        for i, e in enumerate(self.edges):
            if i != 0 and i != 4:
                self.g.remove_edge(e)

        for v in self.nodes:
            self.assertEqual(len(v), 0)
            self.assertEqual(v.nb_neighbors, 0)

    def test_add_edge_add_neighbors(self):

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
            if (u, v) in self.couples:
                self.assertTrue(v.is_neighbor_of(u))
                self.assertTrue(u.is_neighbor_of(v))
            elif (v, u) not in self.couples:
                self.assertFalse(v.is_neighbor_of(u))
                self.assertFalse(u.is_neighbor_of(v))

    def test_add_node_do_not_add_neighbors(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for v2 in self.nodes:
            self.assertFalse(u.is_neighbor_of(v2))
            self.assertFalse(v.is_neighbor_of(v2))
            self.assertFalse(w.is_neighbor_of(v2))
            self.assertFalse(v2.is_neighbor_of(u))
            self.assertFalse(v2.is_neighbor_of(v))
            self.assertFalse(v2.is_neighbor_of(w))

    def test_remove_node_remove_neighbor_of_neighbors(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_node(v1)
        self.assertFalse(v2.is_neighbor_of(v1))
        self.assertFalse(v4.is_neighbor_of(v1))
        self.assertFalse(v5.is_neighbor_of(v1))
        self.assertFalse(v1.is_neighbor_of(v2))
        self.assertFalse(v1.is_neighbor_of(v4))
        self.assertFalse(v1.is_neighbor_of(v5))

    def test_remove_edge_remove_neighbors_of_extremities(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_edge(self.edges[0])
        self.assertFalse(v1.is_neighbor_of(v5))
        self.assertFalse(v5.is_neighbor_of(v1))

        self.g.remove_edge(self.edges[7])
        self.assertFalse(v1.is_neighbor_of(v4))
        self.assertFalse(v4.is_neighbor_of(v1))

    def test_add_edge_add_neighbors_2(self):

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
            if (u, v) in self.couples:
                self.assertIn(u, list(v.neighbors))
                self.assertIn(v, list(u.neighbors))
            elif (v, u) not in self.couples:
                self.assertNotIn(u, list(v.neighbors))
                self.assertNotIn(v, list(u.neighbors))

    def test_add_node_do_not_add_neighbors_2(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for v2 in self.nodes:
            self.assertNotIn(v2, list(u.neighbors))
            self.assertNotIn(v2, list(v.neighbors))
            self.assertNotIn(v2, list(w.neighbors))
            self.assertNotIn(u, list(v2.neighbors))
            self.assertNotIn(v, list(v2.neighbors))
            self.assertNotIn(w, list(v2.neighbors))

    def test_remove_node_remove_neighbor_of_neighbors_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_node(v1)
        self.assertNotIn(v1, list(v2.neighbors))
        self.assertNotIn(v1, list(v4.neighbors))
        self.assertNotIn(v1, list(v5.neighbors))
        self.assertNotIn(v2, list(v1.neighbors))
        self.assertNotIn(v4, list(v1.neighbors))
        self.assertNotIn(v5, list(v1.neighbors))

    def test_remove_edge_remove_neighbors_of_extremities_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_edge(self.edges[0])
        self.assertNotIn(v5, list(v1.neighbors))
        self.assertNotIn(v1, list(v5.neighbors))

        self.g.remove_edge(self.edges[7])
        self.assertNotIn(v4, list(v1.neighbors))
        self.assertNotIn(v1, list(v4.neighbors))

    def test_nb_neighbors_equal_nb_incident_edges(self):
        for v in self.nodes:
            self.assertEqual(v.nb_neighbors, len(list(v.incident_edges)))

    def test_add_edge_add_incident_edge(self):

        for e, couple in zip(self.edges, self.couples):
            u, v = couple
            for w in self.nodes:
                if w != u and w != v:
                    self.assertFalse(w.is_incident_to(e))
                else:
                    self.assertTrue(w.is_incident_to(e))

    def test_new_node_are_not_incident_to_previous_edges(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for e in self.edges:
            self.assertFalse(u.is_incident_to(e))
            self.assertFalse(v.is_incident_to(e))
            self.assertFalse(w.is_incident_to(e))

    def test_remove_node_remove_incident_edges_of_neighbors(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8 = self.edges
        self.g.remove_node(v1)
        self.assertFalse(v2.is_incident_to(e5))
        self.assertFalse(v5.is_incident_to(e1))
        self.assertFalse(v4.is_incident_to(e8))

    def test_remove_edge_remove_incident_edges_extremities(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8 = self.edges
        self.g.remove_edge(e1)
        self.assertFalse(v1.is_incident_to(e1))
        self.assertFalse(v5.is_incident_to(e1))

        self.g.remove_edge(e8)
        self.assertFalse(v1.is_incident_to(e8))
        self.assertFalse(v4.is_incident_to(e8))

    def test_add_edge_add_incident_edge_2(self):

        for e, couple in zip(self.edges, self.couples):
            u, v = couple
            for w in self.nodes:
                if w != u and w != v:
                    self.assertNotIn(e, list(w.incident_edges))
                else:
                    self.assertIn(e, list(w.incident_edges))

    def test_new_node_are_not_incident_to_previous_edges_2(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for e in self.edges:
            self.assertNotIn(e, list(u.incident_edges))
            self.assertNotIn(e, list(v.incident_edges))
            self.assertNotIn(e, list(w.incident_edges))

    def test_remove_node_remove_incident_edges_of_neighbors_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8 = self.edges
        self.g.remove_node(v1)
        self.assertNotIn(e5, list(v2.incident_edges))
        self.assertNotIn(e1, list(v5.incident_edges))
        self.assertNotIn(e8, list(v4.incident_edges))

    def test_remove_edge_remove_incident_edges_extremities_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8 = self.edges
        self.g.remove_edge(e1)
        self.assertNotIn(e1, list(v1.incident_edges))
        self.assertNotIn(e1, list(v5.incident_edges))

        self.g.remove_edge(e8)
        self.assertNotIn(e8, list(v1.incident_edges))
        self.assertNotIn(e8, list(v4.incident_edges))

    def test_add_edge_add_incident_edge_3(self):
        for e, couple in zip(self.edges, self.couples):
            u, v = couple
            self.assertEqual(e, u.get_incident_edge(v))
            self.assertEqual(e, v.get_incident_edge(u))

    def test_get_incident_edge_raise_TypeError_with_not_node(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8 = self.edges

        g2 = DirectedGraph()
        v = g2.add_node()

        with self.assertRaises(TypeError):
            v1.get_incident_edge(1)

        with self.assertRaises(TypeError):
            v1.get_incident_edge('abc')

        with self.assertRaises(TypeError):
            v1.get_incident_edge((v1, v2))

        with self.assertRaises(TypeError):
            v1.get_incident_edge(e5)

        with self.assertRaises(TypeError):
            v1.get_incident_edge(None)

        with self.assertRaises(TypeError):
            v1.get_incident_edge(v)

    def test_get_incident_edge_raise_NodeError_with_not_neighbor(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes

        g2 = UndirectedGraph()
        v = g2.add_node()

        with self.assertRaises(NodeError):
            v1.get_incident_edge(v3)

        with self.assertRaises(NodeError):
            v1.get_incident_edge(v)

    def test_get_incident_edge_raise_NodeError_with_not_neighbor_due_to_remove_edge(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8 = self.edges

        self.g.remove_edge(e1)

        with self.assertRaises(NodeError):
            v1.get_incident_edge(v5)

        with self.assertRaises(NodeError):
            v5.get_incident_edge(v1)

    def test_get_incident_edge_raise_NodeError_with_not_neighbor_due_to_remove_node(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes

        self.g.remove_node(v5)

        with self.assertRaises(NodeError):
            v1.get_incident_edge(v5)


if __name__ == '__main__':

    if CONCURRENTTEST:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestUndirectedNode)
        runner = unittest.TextTestRunner()
        concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests(50))
        runner.run(concurrent_suite)
    else:
        unittest.main()
