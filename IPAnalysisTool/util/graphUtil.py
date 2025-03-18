from graph_tool import Graph, VertexPropertyMap


def mapVerticesByProperty(g1: Graph, g2: Graph, property: str = "ip") -> dict:
    g1_prop = g1.vertex_properties[property]
    g2_prop = g2.vertex_properties[property]
    ip_to_vertex = {}
    for v in g2.vertices():
        ip_val = g2_prop[v]
        ip_to_vertex[ip_val] = v
    mapping = {}
    for v in g1.vertices():
        ip_val = g1_prop[v]
        if ip_val in ip_to_vertex:
            mapping[v] = ip_to_vertex[ip_val]

    return mapping

def get_address_node_map(graph: Graph) -> dict:
    return {graph.vp.ip[v] : v for v in graph.vertices()}