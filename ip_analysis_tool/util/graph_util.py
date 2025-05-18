from graph_tool import Graph, VertexPropertyMap


def map_vertices_by_property(g1: Graph, g2: Graph, property: str = "ip") -> dict:
    """
    Maps vertices between two graphs based on a given property.
    :param g1: First input graph.
    :param g2: Second input graph.
    :param property: Name of the property to map vertices on.
    :return: A map, where a vertex from g1 is mapped to a corresponding vertex from g2.
    """
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
    """
    Maps IP addresses to their corresponding node IDs in a given graph.
    :param graph: Input graph.
    :return: Map of IP addresses to their corresponding node IDs in a given graph.
    """
    return {graph.vp.ip[v] : v for v in graph.vertices()}