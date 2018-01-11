import unittest

from dynamicgraphviz.graph.directedgraph import DirectedGraph
from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph
from dynamicgraphviz.exceptions.graph_errors import GraphError, NodeMembershipError, LinkError, LinkMembershipError, \
    NodeError

CONCURRENTTEST = False
try:
    from concurrencytest import ConcurrentTestSuite, fork_for_tests
    CONCURRENTTEST = True
except ImportError:
    pass


class TestDirectedNode(unittest.TestCase):

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

    def test_add_node_increase_index(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.assertEqual(v1.index + 1, v2.index)
        self.assertEqual(v2.index + 1, v3.index)
        self.assertEqual(v3.index + 1, v4.index)
        self.assertEqual(v4.index + 1, v5.index)
        self.assertEqual(v5.index + 1, v6.index)
        self.assertEqual(v6.index + 1, v7.index)
        self.assertEqual(v7.index + 1, v8.index)

    def test_add_arc_increase_nb_neighbors(self):
        sizes = [3, 3, 3, 3, 1, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(len(v), size)
            self.assertEqual(v.nb_neighbors, size)

    def test_add_arc_increase_nb_input_neighbors(self):
        sizes = [2, 1, 2, 1, 1, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(v.nb_input_neighbors, size)

    def test_add_arc_increase_nb_output_neighbors(self):
        sizes = [2, 3, 2, 3, 0, 0, 0, 0]
        
        for v, size in zip(self.nodes, sizes):
            self.assertEqual(v.nb_output_neighbors, size)

    def test_add_node_do_not_increase_nb_neighbors(self):
        self.g.add_node()
        self.g.add_node()
        self.g.add_node()
        sizes = [3, 3, 3, 3, 1, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(len(v), size)
            self.assertEqual(v.nb_neighbors, size)

    def test_add_node_do_not_increase_nb_input_neighbors(self):
        self.g.add_node()
        self.g.add_node()
        self.g.add_node()
        sizes = [2, 1, 2, 1, 1, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(v.nb_input_neighbors, size)

    def test_add_node_do_not_increase_nb_output_neighbors(self):
        self.g.add_node()
        self.g.add_node()
        self.g.add_node()
        sizes = [2, 3, 2, 3, 0, 0, 0, 0]
        
        for v, size in zip(self.nodes, sizes):
            self.assertEqual(v.nb_output_neighbors, size)

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

    def test_remove_node_decrease_nb_input_neighbors_of_output_neighbors(self):
        self.g.remove_node(self.nodes[0])
        sizes = [0, 2, 1, 0, 1, 1, 1]

        for v, size in zip(self.nodes[1:], sizes):
            self.assertEqual(v.nb_input_neighbors, size)

        self.g.remove_node(self.nodes[5])
        sizes = [0, 2, 1, 0, 1, 1]

        for v, size in zip(self.nodes[1:5]+self.nodes[6:], sizes):
            self.assertEqual(v.nb_input_neighbors, size)

    def test_remove_node_decrease_nb_output_neighbors_of_input_neighbors(self):
        self.g.remove_node(self.nodes[0])
        sizes = [2, 2, 2, 0, 0, 0, 0]

        for v, size in zip(self.nodes[1:], sizes):
            self.assertEqual(v.nb_output_neighbors, size)

        self.g.remove_node(self.nodes[5])
        sizes = [1, 2, 2, 0, 0, 0]

        for v, size in zip(self.nodes[1:5]+self.nodes[6:], sizes):
            self.assertEqual(v.nb_output_neighbors, size)

    def test_remove_arc_decrease_nb_neighbors_of_extremities(self):
        self.g.remove_arc(self.arcs[0])
        sizes = [2, 3, 3, 3, 0, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(len(v), size)
            self.assertEqual(v.nb_neighbors, size)

        for i, e in enumerate(self.arcs):
            if i != 0:
                self.g.remove_arc(e)

        for v in self.nodes:
            self.assertEqual(len(v), 0)
            self.assertEqual(v.nb_neighbors, 0)

    def test_remove_u_v_decrease_nb_neighbors_of_extremities_except_if_v_u_exists(self):
        self.g.remove_arc(self.arcs[4])
        sizes = [3, 3, 3, 3, 1, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(len(v), size)
            self.assertEqual(v.nb_neighbors, size)

    def test_remove_arc_decrease_nb_input_neighbors_of_output_node(self):
        self.g.remove_arc(self.arcs[0])
        sizes = [2, 1, 2, 1, 0, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(v.nb_input_neighbors, size)

        self.g.remove_arc(self.arcs[4])
        sizes = [2, 0, 2, 1, 0, 1, 1, 1]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(v.nb_input_neighbors, size)

        for i, e in enumerate(self.arcs):
            if i != 0 and i != 4:
                self.g.remove_arc(e)

        for v in self.nodes:
            self.assertEqual(v.nb_input_neighbors, 0)

    def test_remove_arc_decrease_nb_output_neighbors_of_input_node(self):
        self.g.remove_arc(self.arcs[0])
        sizes = [1, 3, 2, 3, 0, 0, 0, 0]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(v.nb_output_neighbors, size)

        self.g.remove_arc(self.arcs[4])
        sizes = [0, 3, 2, 3, 0, 0, 0, 0]

        for v, size in zip(self.nodes, sizes):
            self.assertEqual(v.nb_output_neighbors, size)

        for i, e in enumerate(self.arcs):
            if i != 0 and i != 4:
                self.g.remove_arc(e)

        for v in self.nodes:
            self.assertEqual(v.nb_output_neighbors, 0)

    def test_add_arc_add_neighbors(self):

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

    def test_add_arc_add_input_neighbors(self):

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
            if (u, v) in self.couples:
                self.assertTrue(u.is_input_neighbor_of(v))
            elif (v, u) not in self.couples:
                self.assertFalse(u.is_input_neighbor_of(v))

    def test_add_arc_add_output_neighbors(self):

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
            if (u, v) in self.couples:
                self.assertTrue(v.is_output_neighbor_of(u))
            elif (v, u) not in self.couples:
                self.assertFalse(v.is_output_neighbor_of(u))

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

    def test_add_node_do_not_add_input_neighbors(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for v2 in self.nodes:
            self.assertFalse(u.is_input_neighbor_of(v2))
            self.assertFalse(v.is_input_neighbor_of(v2))
            self.assertFalse(w.is_input_neighbor_of(v2))
            self.assertFalse(v2.is_input_neighbor_of(u))
            self.assertFalse(v2.is_input_neighbor_of(v))
            self.assertFalse(v2.is_input_neighbor_of(w))

    def test_add_node_do_not_add_output_neighbors(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for v2 in self.nodes:
            self.assertFalse(u.is_output_neighbor_of(v2))
            self.assertFalse(v.is_output_neighbor_of(v2))
            self.assertFalse(w.is_output_neighbor_of(v2))
            self.assertFalse(v2.is_output_neighbor_of(u))
            self.assertFalse(v2.is_output_neighbor_of(v))
            self.assertFalse(v2.is_output_neighbor_of(w))

    def test_remove_node_remove_neighbor_of_neighbors(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_node(v1)
        self.assertFalse(v2.is_neighbor_of(v1))
        self.assertFalse(v4.is_neighbor_of(v1))
        self.assertFalse(v5.is_neighbor_of(v1))
        self.assertFalse(v1.is_neighbor_of(v2))
        self.assertFalse(v1.is_neighbor_of(v4))
        self.assertFalse(v1.is_neighbor_of(v5))

    def test_remove_node_remove_input_neighbor_of_neighbors(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_node(v1)
        self.assertFalse(v2.is_input_neighbor_of(v1))
        self.assertFalse(v4.is_input_neighbor_of(v1))
        self.assertFalse(v1.is_input_neighbor_of(v2))
        self.assertFalse(v1.is_input_neighbor_of(v5))

    def test_remove_node_remove_output_neighbor_of_neighbors(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_node(v1)
        self.assertFalse(v1.is_output_neighbor_of(v2))
        self.assertFalse(v1.is_output_neighbor_of(v4))
        self.assertFalse(v2.is_output_neighbor_of(v1))
        self.assertFalse(v5.is_output_neighbor_of(v1))

    def test_remove_arc_remove_neighbors_of_extremities(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_arc(self.arcs[0])
        self.assertFalse(v1.is_neighbor_of(v5))
        self.assertFalse(v5.is_neighbor_of(v1))

        self.g.remove_arc(self.arcs[7])
        self.assertFalse(v1.is_neighbor_of(v4))
        self.assertFalse(v4.is_neighbor_of(v1))

    def test_remove_u_v_remove_neighbors_of_extremities_except_if_v_u_exists(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_arc(self.arcs[4])
        self.assertTrue(v1.is_neighbor_of(v2))
        self.assertTrue(v2.is_neighbor_of(v1))

    def test_remove_arc_remove_input_neighbors_of_output_node(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_arc(self.arcs[0])
        self.assertFalse(v1.is_input_neighbor_of(v5))

        self.g.remove_arc(self.arcs[7])
        self.assertFalse(v4.is_input_neighbor_of(v1))

        self.g.remove_arc(self.arcs[4])
        self.assertFalse(v1.is_input_neighbor_of(v2))

    def test_remove_arc_remove_output_neighbors_of_input_node(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_arc(self.arcs[0])
        self.assertFalse(v5.is_output_neighbor_of(v1))

        self.g.remove_arc(self.arcs[7])
        self.assertFalse(v1.is_output_neighbor_of(v4))

        self.g.remove_arc(self.arcs[4])
        self.assertFalse(v2.is_output_neighbor_of(v1))

    def test_add_arc_add_neighbors_2(self):

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
            if (u, v) in self.couples:
                self.assertIn(v, list(u.neighbors))
                self.assertIn(u, list(v.neighbors))
            elif (v, u) not in self.couples:
                self.assertNotIn(v, list(u.neighbors))
                self.assertNotIn(u, list(v.neighbors))

    def test_add_arc_add_input_neighbors_2(self):

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
            if (u, v) in self.couples:
                self.assertIn(u, list(v.input_neighbors))
            elif (v, u) not in self.couples:
                self.assertNotIn(u, list(v.input_neighbors))

    def test_add_arc_add_output_neighbors_2(self):

        for u in self.g:
            for v in self.g:
                if u == v:
                    continue
            if (u, v) in self.couples:
                self.assertIn(v, list(u.output_neighbors))
            elif (v, u) not in self.couples:
                self.assertNotIn(v, list(u.output_neighbors))

    def test_add_node_do_not_add_neighbors_2(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for v2 in self.nodes:
            self.assertNotIn(u, list(v2.neighbors))
            self.assertNotIn(v, list(v2.neighbors))
            self.assertNotIn(w, list(v2.neighbors))
            self.assertNotIn(v2, list(u.neighbors))
            self.assertNotIn(v2, list(v.neighbors))
            self.assertNotIn(v2, list(w.neighbors))

    def test_add_node_do_not_add_input_neighbors_2(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for v2 in self.nodes:
            self.assertNotIn(u, list(v2.input_neighbors))
            self.assertNotIn(v, list(v2.input_neighbors))
            self.assertNotIn(w, list(v2.input_neighbors))
            self.assertNotIn(v2, list(u.input_neighbors))
            self.assertNotIn(v2, list(v.input_neighbors))
            self.assertNotIn(v2, list(w.input_neighbors))

    def test_add_node_do_not_add_output_neighbors_2(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for v2 in self.nodes:
            self.assertNotIn(u, list(v2.output_neighbors))
            self.assertNotIn(v, list(v2.output_neighbors))
            self.assertNotIn(w, list(v2.output_neighbors))
            self.assertNotIn(v2, list(u.output_neighbors))
            self.assertNotIn(v2, list(v.output_neighbors))
            self.assertNotIn(v2, list(w.output_neighbors))

    def test_remove_node_remove_neighbor_of_neighbors_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_node(v1)
        self.assertNotIn(v2, list(v1.neighbors))
        self.assertNotIn(v4, list(v1.neighbors))
        self.assertNotIn(v5, list(v1.neighbors))
        self.assertNotIn(v1, list(v2.neighbors))
        self.assertNotIn(v1, list(v4.neighbors))
        self.assertNotIn(v1, list(v5.neighbors))

    def test_remove_node_remove_input_neighbor_of_neighbors_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_node(v1)
        self.assertNotIn(v2, list(v1.input_neighbors))
        self.assertNotIn(v4, list(v1.input_neighbors))
        self.assertNotIn(v1, list(v2.input_neighbors))
        self.assertNotIn(v1, list(v5.input_neighbors))

    def test_remove_node_remove_output_neighbor_of_neighbors_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_node(v1)
        self.assertNotIn(v1, list(v2.output_neighbors))
        self.assertNotIn(v1, list(v4.output_neighbors))
        self.assertNotIn(v2, list(v1.output_neighbors))
        self.assertNotIn(v5, list(v1.output_neighbors))

    def test_remove_arc_remove_neighbors_of_extremities_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_arc(self.arcs[0])
        self.assertNotIn(v1, list(v5.neighbors))
        self.assertNotIn(v5, list(v1.neighbors))

        self.g.remove_arc(self.arcs[7])
        self.assertNotIn(v1, list(v4.neighbors))
        self.assertNotIn(v4, list(v1.neighbors))

    def test_remove_u_v_remove_neighbors_of_extremities_except_if_v_u_exists_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_arc(self.arcs[4])
        self.assertIn(v1, list(v2.neighbors))
        self.assertIn(v2, list(v1.neighbors))

    def test_remove_arc_remove_input_neighbors_of_output_node_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_arc(self.arcs[0])
        self.assertNotIn(v1, list(v5.input_neighbors))

        self.g.remove_arc(self.arcs[7])
        self.assertNotIn(v4, list(v1.input_neighbors))

        self.g.remove_arc(self.arcs[4])
        self.assertNotIn(v1, list(v2.input_neighbors))

    def test_remove_arc_remove_output_neighbors_of_input_node_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        self.g.remove_arc(self.arcs[0])
        self.assertNotIn(v5, list(v1.output_neighbors))

        self.g.remove_arc(self.arcs[7])
        self.assertNotIn(v1, list(v4.output_neighbors))

        self.g.remove_arc(self.arcs[4])

    def test_nb_neighbors_does_not_equal_nb_incident_arcs_iff_u_v_and_v_u_exists(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        for v in [v5, v6, v7, v8]:
            self.assertEqual(v.nb_neighbors, len(list(v.incident_arcs)))
        for v in [v1, v2, v3, v4]:
            self.assertNotEqual(v.nb_neighbors, len(list(v.incident_arcs)))

    def test_nb_input_arc_plus_nb_output_arc_equal_nb_incident_arcs(self):
        for v in self.nodes:
            self.assertEqual(len(list(v.input_arcs)) + len(list(v.output_arcs)), len(list(v.incident_arcs)))

    def test_add_arc_add_incident_arc(self):

        for a, couple in zip(self.arcs, self.couples):
            u, v = couple
            for w in self.nodes:
                if w != u and w != v:
                    self.assertFalse(w.is_incident_to(a))
                else:
                    self.assertTrue(w.is_incident_to(a))

    def test_add_arc_add_input_arc_of_output_node(self):

        for a, couple in zip(self.arcs, self.couples):
            u, v = couple
            for w in self.nodes:
                if w != v:
                    self.assertFalse(w.is_input_arc(a))
                else:
                    self.assertTrue(w.is_input_arc(a))

    def test_add_arc_add_output_arc_of_input_node(self):

        for a, couple in zip(self.arcs, self.couples):
            u, v = couple
            for w in self.nodes:
                if w != u:
                    self.assertFalse(w.is_output_arc(a))
                else:
                    self.assertTrue(w.is_output_arc(a))

    def test_new_node_are_not_incident_to_previous_arcs(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for e in self.arcs:
            self.assertFalse(u.is_incident_to(e))
            self.assertFalse(v.is_incident_to(e))
            self.assertFalse(w.is_incident_to(e))

    def test_previous_arcs_are_not_input_arcs_of_new_node(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for a in self.arcs:
            self.assertFalse(u.is_input_arc(a))
            self.assertFalse(v.is_input_arc(a))
            self.assertFalse(w.is_input_arc(a))

    def test_previous_arcs_are_not_output_arcs_of_new_node(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for a in self.arcs:
            self.assertFalse(u.is_output_arc(a))
            self.assertFalse(v.is_output_arc(a))
            self.assertFalse(w.is_output_arc(a))

    def test_remove_node_remove_incident_arcs_of_neighbors(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_node(v1)
        self.assertFalse(v2.is_incident_to(e5))
        self.assertFalse(v2.is_incident_to(e9))
        self.assertFalse(v5.is_incident_to(e1))
        self.assertFalse(v4.is_incident_to(e8))

    def test_remove_node_remove_input_arcs_of_neighbors(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_node(v1)
        self.assertFalse(v2.is_input_arc(e5))
        self.assertFalse(v5.is_input_arc(e1))

    def test_remove_node_remove_output_arcs_of_neighbors(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_node(v1)
        self.assertFalse(v2.is_input_arc(e9))
        self.assertFalse(v4.is_input_arc(e8))

    def test_remove_arc_remove_incident_arcs_extremities(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_arc(e1)
        self.assertFalse(v1.is_incident_to(e1))
        self.assertFalse(v5.is_incident_to(e1))

        self.g.remove_arc(e8)
        self.assertFalse(v1.is_incident_to(e8))
        self.assertFalse(v4.is_incident_to(e8))

        self.g.remove_arc(e5)
        self.assertFalse(v1.is_incident_to(e5))
        self.assertFalse(v2.is_incident_to(e5))

    def test_remove_arc_remove_input_arc_of_output_node(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_arc(e1)
        self.assertFalse(v5.is_input_arc(e1))

        self.g.remove_arc(e8)
        self.assertFalse(v4.is_input_arc(e8))

        self.g.remove_arc(e5)
        self.assertFalse(v2.is_input_arc(e5))

    def test_remove_arc_remove_output_arc_of_input_node(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_arc(e1)
        self.assertFalse(v1.is_output_arc(e1))

        self.g.remove_arc(e8)
        self.assertFalse(v1.is_output_arc(e8))

        self.g.remove_arc(e5)
        self.assertFalse(v1.is_output_arc(e5))

    def test_add_arc_add_incident_arc_2(self):

        for a, couple in zip(self.arcs, self.couples):
            u, v = couple
            for w in self.nodes:
                if w != u and w != v:
                    self.assertNotIn(a, list(w.incident_arcs))
                else:
                    self.assertIn(a, list(w.incident_arcs))

    def test_add_arc_add_input_arc_of_output_node_2(self):

        for a, couple in zip(self.arcs, self.couples):
            u, v = couple
            for w in self.nodes:
                if w != v:
                    self.assertNotIn(a, list(w.input_arcs))
                else:
                    self.assertIn(a, list(w.input_arcs))

    def test_add_arc_add_output_arc_of_input_node_2(self):

        for a, couple in zip(self.arcs, self.couples):
            u, v = couple
            for w in self.nodes:
                if w != u:
                    self.assertNotIn(a, list(w.output_arcs))
                else:
                    self.assertIn(a, list(w.output_arcs))

    def test_new_node_are_not_incident_to_previous_arcs_2(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for e in self.arcs:
            self.assertNotIn(e, list(u.incident_arcs))
            self.assertNotIn(e, list(v.incident_arcs))
            self.assertNotIn(e, list(w.incident_arcs))

    def test_previous_arcs_are_not_input_arcs_of_new_node_2(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for a in self.arcs:
            self.assertNotIn(a, list(u.input_arcs))
            self.assertNotIn(a, list(v.input_arcs))
            self.assertNotIn(a, list(w.input_arcs))

    def test_previous_arcs_are_not_output_arcs_of_new_node_2(self):
        u = self.g.add_node()
        v = self.g.add_node()
        w = self.g.add_node()

        for a in self.arcs:
            self.assertNotIn(a, list(u.output_arcs))
            self.assertNotIn(a, list(v.output_arcs))
            self.assertNotIn(a, list(w.output_arcs))

    def test_remove_node_remove_incident_arcs_of_neighbors_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_node(v1)
        self.assertNotIn(e5, list(v2.incident_arcs))
        self.assertNotIn(e9, list(v2.incident_arcs))
        self.assertNotIn(e1, list(v5.incident_arcs))
        self.assertNotIn(e8, list(v4.incident_arcs))

    def test_remove_node_remove_input_arcs_of_neighbors_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_node(v1)
        self.assertNotIn(e5, list(v2.input_arcs))
        self.assertNotIn(e1, list(v5.input_arcs))

    def test_remove_node_remove_output_arcs_of_neighbors_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_node(v1)
        self.assertNotIn(e9, list(v2.input_arcs))
        self.assertNotIn(e8, list(v4.input_arcs))

    def test_remove_arc_remove_incident_arcs_extremities_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_arc(e1)
        self.assertNotIn(e1, list(v1.incident_arcs))
        self.assertNotIn(e1, list(v5.incident_arcs))

        self.g.remove_arc(e8)
        self.assertNotIn(e8, list(v1.incident_arcs))
        self.assertNotIn(e8, list(v4.incident_arcs))

        self.g.remove_arc(e5)
        self.assertNotIn(e5, list(v1.incident_arcs))
        self.assertNotIn(e5, list(v2.incident_arcs))

    def test_remove_arc_remove_input_arc_of_output_node_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_arc(e1)
        self.assertNotIn(e1, list(v5.input_arcs))

        self.g.remove_arc(e8)
        self.assertNotIn(e8, list(v4.input_arcs))

        self.g.remove_arc(e5)
        self.assertNotIn(e5, list(v2.input_arcs))

    def test_remove_arc_remove_output_arc_of_input_node_2(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        self.g.remove_arc(e1)
        self.assertNotIn(e1, list(v1.output_arcs))

        self.g.remove_arc(e8)
        self.assertNotIn(e8, list(v1.output_arcs))

        self.g.remove_arc(e5)
        self.assertNotIn(e5, list(v1.output_arcs))

    def test_add_arc_add_incident_arc_3(self):

        c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = self.couples
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs
        for e, couple in zip([e1, e2, e3, e4, e6, e8], [c1, c2, c3, c4, c6, c8]):
            u, v = couple
            self.assertEqual(e, u.get_incident_arc(v))
            self.assertEqual(e, v.get_incident_arc(u))

    def test_get_incident_arc_return_input_arc_by_default(self):
        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs

        self.assertEqual(e5, v2.get_incident_arc(v1))
        self.assertEqual(e9, v1.get_incident_arc(v2))

    def test_add_arc_add_input_arc_3(self):
        for e, couple in zip(self.arcs, self.couples):
            u, v = couple
            self.assertEqual(e, v.get_input_arc(u))

    def test_add_arc_add_output_arc_3(self):
        for e, couple in zip(self.arcs, self.couples):
            u, v = couple
            self.assertEqual(e, u.get_output_arc(v))

    def test_get_incident_arc_raise_TypeError_with_not_node(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs

        g2 = UndirectedGraph()
        v = g2.add_node()

        with self.assertRaises(TypeError):
            v1.get_incident_arc(1)

        with self.assertRaises(TypeError):
            v1.get_incident_arc('abc')

        with self.assertRaises(TypeError):
            v1.get_incident_arc((v1, v2))

        with self.assertRaises(TypeError):
            v1.get_incident_arc(e5)

        with self.assertRaises(TypeError):
            v1.get_incident_arc(None)

        with self.assertRaises(TypeError):
            v1.get_incident_arc(v)

    def test_get_input_arc_raise_TypeError_with_not_node(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs

        g2 = UndirectedGraph()
        v = g2.add_node()

        with self.assertRaises(TypeError):
            v1.get_input_arc(1)

        with self.assertRaises(TypeError):
            v1.get_input_arc('abc')

        with self.assertRaises(TypeError):
            v1.get_input_arc((v1, v2))

        with self.assertRaises(TypeError):
            v1.get_input_arc(e5)

        with self.assertRaises(TypeError):
            v1.get_input_arc(None)

        with self.assertRaises(TypeError):
            v1.get_input_arc(v)

    def test_get_output_arc_raise_TypeError_with_not_node(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs

        g2 = UndirectedGraph()
        v = g2.add_node()

        with self.assertRaises(TypeError):
            v1.get_output_arc(1)

        with self.assertRaises(TypeError):
            v1.get_output_arc('abc')

        with self.assertRaises(TypeError):
            v1.get_output_arc((v1, v2))

        with self.assertRaises(TypeError):
            v1.get_output_arc(e5)

        with self.assertRaises(TypeError):
            v1.get_output_arc(None)

        with self.assertRaises(TypeError):
            v1.get_output_arc(v)

    def test_get_incident_arc_raise_NodeError_with_not_neighbor(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes

        g2 = DirectedGraph()
        v = g2.add_node()

        with self.assertRaises(NodeError):
            v1.get_incident_arc(v3)

        with self.assertRaises(NodeError):
            v1.get_incident_arc(v)

    def test_get_input_arc_raise_NodeError_with_not_neighbor(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes

        g2 = DirectedGraph()
        v = g2.add_node()

        with self.assertRaises(NodeError):
            v1.get_input_arc(v3)

        with self.assertRaises(NodeError):
            v1.get_input_arc(v5)

        with self.assertRaises(NodeError):
            v1.get_input_arc(v)

    def test_get_output_arc_raise_NodeError_with_not_neighbor(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes

        g2 = DirectedGraph()
        v = g2.add_node()

        with self.assertRaises(NodeError):
            v1.get_output_arc(v3)

        with self.assertRaises(NodeError):
            v1.get_output_arc(v4)

        with self.assertRaises(NodeError):
            v1.get_output_arc(v)

    def test_get_incident_arc_raise_NodeError_with_not_neighbor_due_to_remove_arc(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs

        self.g.remove_arc(e1)

        with self.assertRaises(NodeError):
            v1.get_incident_arc(v5)

        with self.assertRaises(NodeError):
            v5.get_incident_arc(v1)

    def test_get_incident_arc_do_notraise_NodeError_due_to_remove_u_v_if_v_u_exists(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs

        self.g.remove_arc(e5)

        try:
            v1.get_incident_arc(v2)
        except NodeError:
            self.assertFalse(True)

    def test_get_input_arc_raise_NodeError_with_not_neighbor_due_to_remove_arc(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs

        self.g.remove_arc(e1)

        with self.assertRaises(NodeError):
            v5.get_input_arc(v1)

    def test_get_output_arc_raise_NodeError_with_not_neighbor_due_to_remove_arc(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10 = self.arcs

        self.g.remove_arc(e1)

        with self.assertRaises(NodeError):
            v5.get_output_arc(v1)

    def test_get_incident_arc_raise_NodeError_with_not_neighbor_due_to_remove_node(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes

        self.g.remove_node(v5)

        with self.assertRaises(NodeError):
            v1.get_incident_arc(v5)

        self.g.remove_node(v2)

        with self.assertRaises(NodeError):
            v1.get_incident_arc(v2)

    def test_get_input_arc_raise_NodeError_with_not_neighbor_due_to_remove_node(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes

        self.g.remove_node(v2)

        with self.assertRaises(NodeError):
            v1.get_input_arc(v2)

    def test_get_output_arc_raise_NodeError_with_not_neighbor_due_to_remove_node(self):

        v1, v2, v3, v4, v5, v6, v7, v8 = self.nodes

        self.g.remove_node(v5)

        with self.assertRaises(NodeError):
            v1.get_output_arc(v5)

        self.g.remove_node(v2)

        with self.assertRaises(NodeError):
            v1.get_output_arc(v2)


if __name__ == '__main__':

    if CONCURRENTTEST:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestDirectedNode)
        runner = unittest.TextTestRunner()
        concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests(50))
        runner.run(concurrent_suite)
    else:
        unittest.main()
