import graph_tool.all as gt
import os
from numpy import size
from typing import Set
from json import dumps

def edges_on_road(date: str, endpoint_addresses: Set[str], do_shortest_only : bool = False):
    try:
        g : gt.Graph = gt.load_graph(os.path.expanduser(f"~/.cache/IPAnalysisTool/graphs/week/{date}.gt"))
    except:
        raise FileNotFoundError("Graph file not found.")
    endpoints = []
    for v in g.vertices():
        if g.vp.position_in_route[v] == 1:
            startpoint = v
        if g.vp.ip[v] in endpoint_addresses:
            endpoints.append(v)
    edges = g.get_edges()
    edges_amount = size(edges)
    found_edges = set()
    # If we only recognize the shortest path
    if(do_shortest_only):
        for endpoint in endpoints:
            path = gt.shortest_path(g, source = startpoint, target = endpoint, weights=g.ep.minEdge)
            found_edges.update(set(path[1]))
    # If we recognize all paths
    else:
        for endpoint in endpoints:
            paths = gt.all_paths(g, source = startpoint, target = endpoint)
            for path in paths:
                for edge in path:
                    found_edges.add(edge)
    return {
        "endpoints": list(map(lambda endpointAddress: endpointAddress, endpoint_addresses)),
        "edge_amount": len(found_edges),
        "edge_amount_percentage": len(found_edges) / edges_amount * 100,
    }

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    parser.add_argument("-e", "--endpoints", nargs='+', help="The ending points of the edge.")
    parser.add_argument("-s", "--shortest", action="store_true", help="Only recognize the shortest path.")
    args = parser.parse_args()
    print(dumps(edges_on_road(args.date, set(args.endpoints), args.shortest), indent=2))

if __name__ == "__main__":
    main()
