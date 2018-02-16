""" Provide useful algorithms to compute shortest paths in unweighted graph (breadth first search) """

__author__ = "Dimitri Watel"
__copyright__ = "Copyright 2018, dynamicgraphviz"


def breadth_first_search_distances(g, v):
    """
    Return, for each node u, the breadth first search distance from v to u in the graph g.

    For each node u, returns the distance of a shortest path from v to u in an undirected unweighted graph using the
    breadth first search algorithm.

    :param g: an undirected graph
    :param v: a node of g
    :return: a dictionnary associating for each node u the distance of a shortest path from v to u in g
    """

    to_visit = [v]
    visited = set()
    dist = {v: 0}

    while len(to_visit) != 0:
        u = to_visit.pop(0)
        visited.add(u)
        for v in u.neighbors:
            if v in visited:
                continue
            if v not in dist or dist[v] > dist[u] + 1:
                dist[v] = dist[u] + 1
            to_visit.append(v)

    return dist
