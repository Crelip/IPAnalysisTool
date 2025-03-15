import graph_tool.all as gt

def addInverseEP(g: gt.Graph):
    inverse = g.new_edge_property("float")
    g.edge_properties["minEdgeInverse"] = inverse
    for e in g.edges():
        inverse[e] = 1 / g.ep.minEdge[e]
    return g

def makeUndirectedGraph(g: gt.Graph):
    g_new = gt.Graph(directed=True)
    g_new.add_vertex(g.num_vertices())

    # To avoid adding both reciprocal edges, we use a set to track pairs we've already added.
    added = set()

    for e in g.edges():
        u = int(e.source())
        v = int(e.target())
        # Check if the reciprocal edge was already added.
        if (v, u) in added:
            continue
        # Otherwise, add this edge and mark the pair.
        g_new.add_edge(g_new.vertex(u), g_new.vertex(v))
        added.add((u, v))
    return g_new