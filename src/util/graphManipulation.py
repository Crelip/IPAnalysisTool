import graph_tool.all as gt

def addInverseEP(g: gt.Graph):
    inverse = g.new_edge_property("float")
    g.edge_properties["minEdgeInverse"] = inverse
    for e in g.edges():
        inverse[e] = 1 / g.ep.minEdge[e]
    return g