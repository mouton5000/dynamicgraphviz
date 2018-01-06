from dynamicgraphviz.gui.graphDrawer import GraphDrawer, NODE_LINE_WIDTH
from dynamicgraphviz.graph.directedgraph import DirectedGraph


def roy_wharshall(g, gd):
    for w in g:
        gd.set_color(w, (255, 0, 0))
        gd.set_line_width(w, 10)
        for u in g:
            if u == w:
                continue
            gd.set_color(u, (0, 0, 255))
            gd.set_line_width(u, 10)
            for v in g:
                if v == w:
                    continue
                if u == v or u.is_input_neighbor_of(v):
                    continue
                gd.set_color(v, (0, 255, 0))
                gd.set_line_width(v, 10)
                gd.pause()
                if u.is_input_neighbor_of(w) and w.is_input_neighbor_of(v):
                    g.add_arc(u, v)
                    gd.pause()
                gd.set_color(v, (0, 0, 0))
                gd.set_line_width(v, NODE_LINE_WIDTH)
            gd.set_color(u, (0, 0, 0))
            gd.set_line_width(u, NODE_LINE_WIDTH)
        gd.set_color(w, (0, 0, 0))
        gd.set_line_width(w, NODE_LINE_WIDTH)


if __name__ == '__main__':
    g = DirectedGraph()

    v1 = g.add_node()
    v2 = g.add_node()
    v3 = g.add_node()
    v4 = g.add_node()
    v5 = g.add_node()
    v6 = g.add_node()

    a1 = g.add_arc(v1, v2)
    a2 = g.add_arc(v1, v5)
    a3 = g.add_arc(v2, v3)
    a4 = g.add_arc(v4, v1)
    a5 = g.add_arc(v4, v3)
    a6 = g.add_arc(v5, v2)
    a7 = g.add_arc(v5, v3)
    a8 = g.add_arc(v5, v4)
    a9 = g.add_arc(v5, v6)

    gd = GraphDrawer(g)
    gd.place_nodes(doanimate=True)
    roy_wharshall(g, gd)

    gd.pause()
