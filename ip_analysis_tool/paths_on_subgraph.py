from typing import TypedDict
from graph_tool import Graph


class PathsOnSubgraphResult(TypedDict):
    subgraph_routes_count: int
    original_routes_count: int
    ratio: float


def paths_on_subgraph(subgraph: Graph, graph: Graph) -> PathsOnSubgraphResult:
    """
    Calculate the ratio of routes in a subgraph to the routes in the original graph.
    :param subgraph: Subgraph of the graph to calculate the routes from.
    :param graph: Input graph.
    :return: A dict containing the count of routes in the subgraph, the count of routes in the original graph, and the ratio of the two.
    """
    from graph_tool.util import find_vertex
    subgraph_routes = set()
    for v in subgraph.vertices():
        subgraph_routes.update(subgraph.vp.routes[v])
    original_routes_count = len(graph.vp.routes[
        list(find_vertex(graph, graph.vp.position_in_route, 1))[0]
    ])
    return {
        "subgraph_routes_count": len(subgraph_routes),
        "original_routes_count": original_routes_count,
        "ratio": len(subgraph_routes) / original_routes_count
    }
