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


class TestArc(unittest.TestCase):

    def setUp(self):
        self.g = DirectedGraph()
        v1 = self.g.add_node()
        v2 = self.g.add_node()
        v3 = self.g.add_node()
        v4 = self.g.add_node()
        v5 = self.g.add_node()
        v6 = self.g.add_node()
        v7 = self.g.add_node()
        v8 = self.g.add_node()
        self.nodes = [v1, v2, v3, v4, v5, v6, v7, v8]

        self.couples = [(v1, v5), (v2, v6), (v3, v7), (v4, v8), (v1, v2), (v2, v3), (v3, v4), (v4, v1), (v2, v1),
                        (v4, v3)]
        self.arcs = [self.g.add_arc(u, v) for u, v in self.couples]

    def test_arc_is_directed(self):

        for e in self.arcs:
            self.assertTrue(e.directed)

    def test_arc_extremities_are_nodes_defined_by_add_arc_in_the_same_order(self):

        for e, couple in zip(self.arcs, self.couples):
            c1 = list(e.extremities)
            c2 = list(couple)
            self.assertEqual(c1, c2)

    def test_arc_input_node_is_first_node_defined_by_add_arc(self):

        for e, couple in zip(self.arcs, self.couples):
            u, v = couple
            self.assertEqual(e.input_node, u)

    def test_arc_output_node_is_second_node_defined_by_add_arc(self):

        for e, couple in zip(self.arcs, self.couples):
            u, v = couple
            self.assertEqual(e.output_node, v)

    def test_neighbor_return_other_extremity_of_arc(self):

        for e, couple in zip(self.arcs, self.couples):
            u, v = couple
            self.assertEqual(u, e.neighbor(v))
            self.assertEqual(v, e.neighbor(u))

    def test_neighbor_raise_TypeError_with_not_node(self):
        u = self.g.add_node()
        v = self.g.add_node()
        e = self.g.add_arc(u, v)

        e1 = self.arcs[0]

        with self.assertRaises(TypeError):
            e1.neighbor(1)

        with self.assertRaises(TypeError):
            e1.neighbor('abc')

        with self.assertRaises(TypeError):
            e1.neighbor((u, v))

        with self.assertRaises(TypeError):
            e1.neighbor(None)

        with self.assertRaises(TypeError):
            e1.neighbor(e)

    def test_neighbor_raise_LinkError_with_not_extremity(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        u = self.g.add_node()

        g2 = UndirectedGraph()
        w = g2.add_node()

        e1 = self.arcs[0]

        for v in self.nodes:
            if v == v1 or v == v5:
                continue

            with self.assertRaises(LinkError):
                e1.neighbor(v)

        with self.assertRaises(LinkError):
            e1.neighbor(u)

        with self.assertRaises(LinkError):
            e1.neighbor(w)


if __name__ == '__main__':

    if CONCURRENTTEST:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestUndirectedNode)
        runner = unittest.TextTestRunner()
        concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests(50))
        runner.run(concurrent_suite)
    else:
        unittest.main()
