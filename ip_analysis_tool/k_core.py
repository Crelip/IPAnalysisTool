from typing import TypedDict
from graph_tool import Graph, VertexPropertyMap

from collections import defaultdict

from ip_analysis_tool.util.graph_getter import get_graph_by_date
from .util.date_util import get_date_string

class KCoreDecompositionResult(TypedDict):
    """
    KCoreDecompositionResult is a dictionary containing the result of the k-core decomposition.
    :param graph: The corresponding graph. (graph_tool.Graph)
    :param k_core_decomposition: The k-core decomposition of the graph. (graph_tool.VertexPropertyMap)
    :param max_k: The maximum k-core value. (int)
    """
    graph: Graph
    k_core_decomposition: VertexPropertyMap
    max_k: int

class KCoreDecompositionMetadataEntry(TypedDict):
    kcore: int
    count: int
    IPs: list[str]

class KCoreDecompositionMetadata(TypedDict):
    date: str
    max_k: int
    decomposition: list[KCoreDecompositionMetadataEntry]


def k_core_decomposition(g: Graph) -> KCoreDecompositionResult:
    """
    Perform k-core decomposition on the given graph.
    :param g: The graph to perform k-core decomposition on. (graph_tool.Graph)
    :return: (dict) A dictionary containing the input graph, the k-core decomposition, and the maximum k-core value. (KCoreDecompositionResult)
    """
    from .util.graph_manipulation import remove_reciprocal_edges
    from graph_tool.all import kcore_decomposition
    # Do k-core decomposition on a version of the graph without reciprocal edges
    tmp_g = remove_reciprocal_edges(g)
    k_core_prop = kcore_decomposition(tmp_g)
    groups = defaultdict(list)
    max_k = 0
    for v in g.vertices():
        k = k_core_prop[v]
        groups[k].append(g.vp.ip[v])
        if k > max_k: max_k = k
    return {
        "graph": g,
        "k_core_decomposition": k_core_prop,
        "max_k": max_k,
    }

def get_k_core(k_core_data: KCoreDecompositionResult, k : int):
    """
    Get the k-core subgraph of the given graph for a given k.
    :param k_core_data:
    :param k:
    :return:
    """
    from graph_tool import GraphView
    vfilt = k_core_data["graph"].new_vertex_property("bool")
    for v in k_core_data["graph"].vertices(): vfilt[v] = k_core_data["k_core_decomposition"][v] >= k
    return GraphView(k_core_data["graph"], vfilt=vfilt)

def get_max_k_core(k_core_data: KCoreDecompositionResult):
    """
    Get the maximum k-core subgraph of the given graph.
    :param k_core_data:
    :return:
    """
    return get_k_core(k_core_data, k_core_data["max_k"])

def get_k_core_metadata(k_core_data: KCoreDecompositionResult) -> dict:
    """
    Get the metadata for the k-core decomposition in a dict form.
    :param k_core_data:
    :return:
    """
    from json import loads
    groups = defaultdict(list)
    for v in k_core_data["graph"].vertices():
        k = k_core_data["k_core_decomposition"][v]
        groups[k].append(k_core_data["graph"].vp.ip[v])
    return {
        "date": loads(k_core_data.gp.metadata)["date"],
        "max_k": k_core_data["max_k"],
        "decomposition": [
            {
                "kcore": i,
                "count": len(groups[i]),
                "IPs": groups[i]
            } for i in range(k_core_data["max_k"] + 1) if i in groups.keys()
        ]
    }

def main(args=None):
    from argparse import ArgumentParser
    from json import dumps
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    parser.add_argument("-i", "--interval", type=str, help="Generates data for the given time interval. Can choose from: week, month, year, all")
    parser.add_argument("-w", "--weighted_edges", action="store_true", help="Use graphs weighted edges.")

    # Output specifiers
    parser.add_argument("-s", "--visualize", action="store_true", help="Visualize the k-core decomposition.")
    parser.add_argument("-m", "--map_visualize", action="store_true", help="Visualize the k-core decomposition on the world map.")
    parser.add_argument("-o", "--output", type=str, metavar="FILE", help="Output the k-core decomposition results (excluding the graph) to a file.")
    parser.add_argument("-p", "--print", action="store_true", help="Print the k-core decomposition result (excluding the graph) on stdout.")
    parser.add_argument("-g", "--graph", type=str, metavar="FILE", help="Output the resulting graph in the form of a .gt file.")
    args = parser.parse_args(args)
    data = k_core_decomposition(get_graph_by_date(args.date, weighted_edges=args.weighted_edges, time_interval = args.interval))
    if args.visualize:
        from .visualize import visualize_graph
        visualize_graph(data["graph"], f"k-core-{get_date_string(data['date'])}")
    if args.map_visualize:
        from .visualize import visualize_graph_world
        visualize_graph_world(data["graph"], f"k-core-{get_date_string(data['date'])}")
    if args.output:
        with open(args.output[0], "w") as f:
            f.write(dumps(data, indent=2))
    if args.graph:
        filtered_graph = get_k_core(data["graph"], data["max_k"])
        filtered_graph.save(f"{args.graph}.gt")
    if args.print:
        print(data)


if __name__ == "__main__":
    main()