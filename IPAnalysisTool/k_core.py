from graph_tool import Graph
import datetime
from collections import defaultdict

from IPAnalysisTool.util.graph_getter import get_graph_by_date
from .util.week_util import get_date_string

def k_core_decomposition(g: Graph) -> dict:
    from .util.graph_manipulation import remove_reciprocal_edges
    from graph_tool.all import kcore_decomposition
    # Do k-core decomposition on an undirected version of the graph
    g = remove_reciprocal_edges(g)
    k_core_prop = kcore_decomposition(g)
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

def get_k_core(k_core_data: dict, k : int):
    from graph_tool import GraphView
    vfilt = k_core_data["graph"].new_vertex_property("bool")
    for v in k_core_data["graph"].vertices(): vfilt[v] = k_core_data["k_core_decomposition"][v] >= k
    return GraphView(k_core_data["graph"], vfilt=vfilt)

def get_max_k_core(k_core_data: dict):
    return get_k_core(k_core_data, k_core_data["max_k"])

def get_k_core_metadata(k_core_data: dict):
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
    parser.add_argument("-s", "--visualize", action="store_true", help="Visualize the k-core decomposition.")
    parser.add_argument("-m", "--map_visualize", action="store_true", help="Visualize the k-core decomposition on the world map.")
    parser.add_argument("-o", "--output", nargs=1, help="Output the k-core decomposition.")
    parser.add_argument("-p", "--print", action="store_true", help="Print the k-core decomposition on stdout.")
    args = parser.parse_args(args)
    data = k_core_decomposition(get_graph_by_date(args.date))
    if args.visualize:
        from .visualize import visualize_graph
        visualize_graph(data["graph"], f"k-core-{get_date_string(data['date'])}")
    if args.map_visualize:
        from .visualize import visualize_graph_world
        visualize_graph_world(data["graph"], f"k-core-{get_date_string(data['date'])}")
    if args.output:
        with open(args.output[0], "w") as f:
            f.write(dumps(data, indent=2))
    if args.verbose:
        print(data)


if __name__ == "__main__":
    main()