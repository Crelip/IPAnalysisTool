from math import floor
from graph_tool import Graph, VertexPropertyMap

def get_h_index(g : Graph, values : VertexPropertyMap) -> int:
    n = g.num_edges()
    freq = [0] * (n + 1)
    for item in g.edges():
        v = floor(values[item])
        if v >= n: freq[n] += 1
        else: freq[v] += 1
    cumulative = 0
    for h in range(n, -1, -1):
        cumulative += freq[h]
        if cumulative >= h:
            return h
    return 0


def calculate_diameter(graph, weights=None) -> float:
    """
    Calculate the diameter of a graph.
    :param graph: The graph to calculate the diameter of.
    :param weights: The weights to use for the graph. Default is None, all edges will then have weight of 1.
    :return: The diameter of the graph. (float)
    """
    from graph_tool.all import shortest_distance
    from sortedcontainers import SortedSet
    shortest_distances = shortest_distance(graph, directed=False, weights=weights)
    return SortedSet(max(shortest_distances[v]) for v in graph.vertices())[-1]