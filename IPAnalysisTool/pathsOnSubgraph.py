from graph_tool import Graph
def paths_on_subgraph(subgraph : Graph, graph : Graph):
    from graph_tool.util import find_vertex
    subgraph_routes = set()
    for v in subgraph.vertices(): subgraph_routes.update(subgraph.vp.routes[v])
    # All routes start from 127.0.0.1
    original_routes_count = len(graph.vp.routes[
        list(find_vertex(graph, graph.vp.ip, "127.0.0.1"))[0]
                                ])
    return {
        "subgraph_routes_count": len(subgraph_routes),
        "original_routes_count": original_routes_count,
        "ratio": len(subgraph_routes)/original_routes_count
    }