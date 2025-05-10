from graph_tool import Graph

def remove_reciprocal_edges(g: Graph):
    g_new = g.copy()
    # Remove all edges
    edge_removal = g_new.new_edge_property("bool")
    g_new.set_edge_filter(edge_removal)

    # To avoid adding both reciprocal edges, we use a set to track pairs we've already added.
    added = set()

    for e in g.edges():
        u = e.source()
        v = e.target()
        # Check if the reciprocal edge was already added.
        if (v, u) in added or (u, v) in added:
            continue
        # Otherwise, add this edge and mark the pair.
        g_new.add_edge(u, v)
        added.add((u, v))
    return g_new


def continous_subgraph(disconnected_graph : Graph, base_graph : Graph, weight = None):
    from itertools import combinations
    from graph_tool.all import Graph, shortest_distance, min_spanning_tree
    from ip_analysis_tool.util.graph_util import map_vertices_by_property
    '''
    Returns a continuous subgraph from a disconnected graph
    :param disconnected_graph: a subgraph of base_graph
    :param base_graph: the base graph, should be connected (at least in undirected context)
    :return:
    '''
    ip_map = map_vertices_by_property(disconnected_graph, base_graph)
    terminals = [ip_map[v] for v in disconnected_graph.vertices()]

    if weight is None:
        weight = base_graph.new_edge_property("double")
        for e in base_graph.edges():
            weight[e] = 1.0

    # Shortest paths for each terminal
    dist_maps = {}
    pred_maps = {}
    for t in terminals:
        dist, pred = shortest_distance(base_graph, source=t, weights=weight, pred_map=True, directed=False)
        dist_maps[t] = dist
        pred_maps[t] = pred

    # Closure over terminals
    metric_edges = {}
    for u, v in combinations(terminals, 2):
        d = dist_maps[u][v]
        metric_edges[(u, v)] = d
        metric_edges[(v, u)] = d

    # MST with union-find
    parent = {t: t for t in terminals}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    sorted_pairs = sorted(metric_edges.items(), key=lambda item: item[1])
    mst_terminal_edges = []
    added = set()
    for (u, v), d in sorted_pairs:
        if (u, v) in added or (v, u) in added:
            continue
        if find(u) != find(v):
            union(u, v)
            mst_terminal_edges.append((u, v))
            added.add((u, v))

    # Reconstructing MST using Steiner tree algorithm
    steiner_edges = set()
    for u, v in mst_terminal_edges:
        path = []
        current = v
        while current != u:
            pred = pred_maps[u][current]
            if pred is None or pred == -1 or pred == current:
                print("Something went wrong")
                break
            path.append((pred, current))
            current = pred
        steiner_edges.update(path)


    used_vertices = set()
    for u, v in steiner_edges:
        used_vertices.add(u)
        used_vertices.add(v)

    steiner_subgraph = Graph(directed=base_graph.is_directed())
    steiner_subgraph.vp["ip"] = steiner_subgraph.new_vertex_property("string")
    vertex_map = {}
    for v in used_vertices:
        vertex_map[v] = steiner_subgraph.add_vertex()
        steiner_subgraph.vp["ip"][vertex_map[v]] = base_graph.vp["ip"][v]

    steiner_weight = steiner_subgraph.new_edge_property("double")
    for u, v in steiner_edges:
        e = base_graph.edge(u, v)
        if e is None:
            e = base_graph.edge(v, u)
        if e is not None:
            new_e = steiner_subgraph.add_edge(vertex_map[u], vertex_map[v])
            steiner_weight[new_e] = weight[e]


    mst_prop = min_spanning_tree(steiner_subgraph, weights=steiner_weight)
    mst_edge_set = {e for e in steiner_subgraph.edges() if mst_prop[e]}

    # Start building the final subgraph using only the MST edges.
    final_subgraph = Graph(directed=steiner_subgraph.is_directed())
    final_subgraph.vp["ip"] = final_subgraph.new_vertex_property("string")
    final_vertex_map = {}
    for v in steiner_subgraph.vertices():
        final_vertex_map[int(v)] = final_subgraph.add_vertex()
        final_subgraph.vp["ip"][final_vertex_map[int(v)]] = steiner_subgraph.vp["ip"][v]
    final_weight = final_subgraph.new_edge_property("double")
    for e in steiner_subgraph.edges():
        if e in mst_edge_set:
            u = e.source()
            v = e.target()
            new_e = final_subgraph.add_edge(final_vertex_map[int(u)], final_vertex_map[int(v)])
            final_weight[new_e] = steiner_weight[e]

    # Add all edges from disconnected_graph
    disconnected_final_map = map_vertices_by_property(disconnected_graph, final_subgraph)
    for e in disconnected_graph.edges():
        final_subgraph.add_edge(disconnected_final_map[e.source()], disconnected_final_map[e.target()])

    return remove_reciprocal_edges(final_subgraph)

def merge_subgraphs(disconnected_graph_1 : Graph, disconnected_graph_2 : Graph, base_graph : Graph) -> Graph:
    from .graph_util import get_address_node_map
    disconnected_graph = Graph(directed = False)
    disconnected_graph.vp["ip"] = disconnected_graph.new_vertex_property("string")
    addresses = set()
    addresses.update(disconnected_graph_1.vp["ip"][v] for v in disconnected_graph_1.vertices())
    addresses.update(disconnected_graph_2.vp["ip"][v] for v in disconnected_graph_2.vertices())
    for address in addresses:
        new_vertex = disconnected_graph.add_vertex()
        disconnected_graph.vp["ip"][new_vertex] = address
    vertex_map = get_address_node_map(disconnected_graph)
    for e in disconnected_graph_1.edges():
        disconnected_graph.add_edge(
            vertex_map[disconnected_graph_1.vp.ip[e.source()]],
            vertex_map[disconnected_graph_1.vp.ip[e.target()]]
        )
    for e in disconnected_graph_2.edges():
        disconnected_graph.add_edge(
            vertex_map[disconnected_graph_2.vp.ip[e.source()]],
            vertex_map[disconnected_graph_2.vp.ip[e.target()]]
        )
    return continous_subgraph(disconnected_graph, base_graph)
