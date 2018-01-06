from dynamicgraphviz.gui.graphDrawer import GraphDrawer
from dynamicgraphviz.graph.directedgraph import DirectedGraph


def dijkstra(g, weights, s, drawer):

    default = sum(sum(wu.values()) for wu in weights.values()) + 1
    d = {node: default for node in g.nodes}
    d[s] = 0
    x = list(g.nodes)

    for a in g.arcs:
        u, v = a.extremities
        drawer.set_label(a, str(weights[u][v]))

    def draw_dists():
        for v in g.nodes:
            if d[v] != default:
                drawer.set_label(v, str(d[v]))
            else:
                drawer.set_label(v, 'inf')

    def pause():
        drawer.pause()

    draw_dists()
    pause()

    while len(x) != 0:

        u = min(x, key=lambda v: d[v])
        x.remove(u)

        drawer.set_node_color_fill(u, (255, 0, 255))

        for v in u.output_neighbors:
            if v not in x:
                continue

            drawer.set_node_color_fill(v, (255, 255, 0))
            pause()

            if d[v] == -1 or d[v] > d[u] + weights[u][v]:
                d[v] = d[u] + weights[u][v]

                drawer.set_label(v, str(d[v]))
                drawer.set_node_color_fill(v, (255, 255, 255))

        pause()

        if u is not None:
            drawer.set_node_color_fill(u, (0, 0, 255))

    pause()

    return d


def dijkstra2(g, weights, s, gd):

    flows = {a: 0 for a in g.arcs}
    d = {s: 0}

    gd.set_color(s, (255, 0, 255))
    for a in g.arcs:
        u, v = a.extremities
        gd.set_label(a, '0/' + str(weights[u][v]))
        gd.set_line_width(a, 1)

    for v in g.nodes:
        gd.set_label(v, '?')

    gd.set_label(s, '0')

    def uncomplete(a):
        u, v = a.extremities
        return flows[a] < weights[u][v]

    while any(uncomplete(a) for a in g.arcs):
        dp = {}

        gd.pause()

        for v in d:
            for a in v.output_arcs:
                u, v = a.extremities
                w = weights[u][v]
                if flows[a] < w:
                    flows[a] += 1
                    gd.set_label(a, str(flows[a]) + '/' + str(w))
                    gd.set_line_width(a, flows[a])
                if flows[a] == w and v not in d:
                    dp[v] = d[u] + w
                    gd.set_label(v, str(dp[v]))
                    gd.set_color(v, (255, 0, 255))

        d.update(dp)

    gd.pause()

    return d


if __name__ == '__main__':
    g = DirectedGraph()

    v1 = g.add_node()
    v2 = g.add_node()
    v3 = g.add_node()
    v4 = g.add_node()
    v5 = g.add_node()
    v6 = g.add_node()

    weights = {
        v1: {v2: 10, v5: 5},
        v2: {v3: 1},
        v3: {},
        v4: {v1: 7, v3: 6},
        v5: {v2: 3, v3: 4, v4: 2, v6: 3}
    }

    for u in weights:
        for v in weights[u]:
            g.add_arc(u, v)

    gd = GraphDrawer(g)
    gd.place_nodes(doanimate=True)
    d = dijkstra2(g, weights, v1, gd)
    print(d)
