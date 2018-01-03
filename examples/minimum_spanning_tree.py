__author__ = "Dimitri Watel"
__copyright__ = "Copyright 2018, dynamicgraphviz"
__credits__ = ["Dimitri Watel"]
__license__ = "MIT"
__version__ = "0.99"
__maintainer__ = "Dimitri Watel"
__email__ = "patatemouton@gmail.com"
__status__ = "Development"


from gui.graphDrawer import GraphDrawer, LINK_LINE_WIDTH
from graph import UndirectedGraph
from collections import defaultdict


def prim(g, weights, gd):
    if len(g) == 0:
        return None

    v = next(g.nodes)
    visited = [v]
    gd.set_color(v, (255, 0, 255))
    gd.set_line_width(v, 10)
    msp = []

    def w(e):
        u, v = e.extremities
        return weights[u][v]

    gd.pause()
    for _ in range(len(g) - 1):
        e = min((e for v in visited for e in v.incident_edges if e.neighbor(v) not in visited), key=w)
        u, v = e.extremities
        if v in visited:
            visited.append(u)
            gd.set_color(u, (255, 0, 255))
            gd.set_line_width(u, 10)
        else:
            visited.append(v)
            gd.set_color(v, (255, 0, 255))
            gd.set_line_width(v, 10)

        msp.append(e)
        gd.set_color(e, (0, 255, 255))
        gd.set_line_width(e, 10)

        gd.pause()

    return msp


def kruskal(g, weights, gd):

    edges = list(g.edges)

    def w(e):
        u, v = e.extremities
        return weights[u][v]

    edges.sort(key=w)

    components = {}
    for v in g:
        components[v] = v.index

    msp = []

    gd.pause()

    while len(msp) != len(g) - 1:
        e = edges.pop(0)

        gd.set_color(e, (255, 0, 255))
        gd.set_line_width(e, 10)

        gd.pause()

        u, v = e.extremities
        cu = components[u]
        cv = components[v]
        if cu != cv:
            msp.append(e)
            gd.set_color(e, (0, 255, 255))
            gd.set_line_width(e, 10)
            for w in g:
                if components[w] == cv:
                    components[w] = cu
                    gd.set_label(w, str(cu))
        else:
            gd.set_color(e, (0, 0, 0))
            gd.set_line_width(e, LINK_LINE_WIDTH)

        gd.pause()

    return msp


if __name__ == '__main__':
    g = UndirectedGraph()

    v1 = g.add_node()
    v2 = g.add_node()
    v3 = g.add_node()
    v4 = g.add_node()
    v5 = g.add_node()
    v6 = g.add_node()
    v7 = g.add_node()
    v8 = g.add_node()

    weights = defaultdict(dict)
    weights.update({
        v1: {v2: 4, v5: 6},
        v2: {v3: 10, v6: 1},
        v3: {v4: 9, v7: 4},
        v4: {v8: 2},
        v5: {v6: 10},
        v6: {v7: 9},
        v7: {v8: 4},
    })

    waux = defaultdict(dict)
    for u in weights:
        for v in weights[u]:
            g.add_edge(u, v)
            waux[v][u] = weights[u][v]
    for v in waux:
        weights[v].update(waux[v])

    gd = GraphDrawer(g)
    gd.move_node(v1, 100, 100)
    gd.move_node(v2, 300, 100)
    gd.move_node(v3, 500, 100)
    gd.move_node(v4, 700, 100)
    gd.move_node(v5, 100, 200)
    gd.move_node(v6, 300, 200)
    gd.move_node(v7, 500, 200)
    gd.move_node(v8, 700, 200)

    for e in g.edges:
        u, v = e.extremities
        gd.set_label(e, str(weights[u][v]))

    gd.redraw()
    t = kruskal(g, weights, gd)
    print(t)
