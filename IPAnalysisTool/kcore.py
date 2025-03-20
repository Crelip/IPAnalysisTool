from graph_tool import Graph
import datetime
from collections import defaultdict

from .util.graphGetter import getGraphByDate
from .util.graphManipulation import removeReciprocalEdges
from .util.weekUtil import getDateObject, getDateString
from json import loads


def kCoreDecompositionFromDate(date: datetime.date, weighted=False, **kwargs):
    try:
        return kCoreDecomposition(getGraphByDate(date, weighted), **kwargs)
    except KeyError:
        return None

def kCoreDecomposition(g: Graph, **kwargs):
    from graph_tool.all import kcore_decomposition
    output = kwargs.get("output") or "json"
    # Do k-core decomposition on an undirected version of the graph
    g = removeReciprocalEdges(g)
    kCore = kcore_decomposition(g)
    groups = defaultdict(list)
    metadata = loads(g.gp.metadata)
    maxK = 0
    for v in g.vertices():
        k = kCore[v]
        groups[k].append(g.vp.ip[v])
        if k > maxK: maxK = k
    result = {
        "date": metadata["date"],
        "maxK": maxK,
        "decomposition": [
            {
                "kcore": i,
                "count": len(groups[i]),
                "IPs": groups[i]
            } for i in range(maxK + 1) if i in groups.keys()
        ]
    } if output == "json" \
        else [g, kCore, getDateObject(metadata["date"]), maxK] \
        if output == "graph" \
        else None
    return result

def visualizeKCoreDecomposition(date: datetime.date):
    from graph_tool import GraphView
    from .visualize import visualize_graph, visualize_graph_world
    g, kCore, date, k = kCoreDecompositionFromDate(date, output="graph")
    maxK = max([kCore[v] for v in g.vertices()])
    vfilt = g.new_vertex_property("bool")
    for v in g.vertices(): vfilt[v] = kCore[v] == maxK
    gv = GraphView(g, vfilt=vfilt)
    visualize_graph(gv, f"kcore_{getDateString(date)}")

def main(args=None):
    from argparse import ArgumentParser
    from json import dumps
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    parser.add_argument("-s", "--visualize", action="store_true", help="Visualize the k-core decomposition.")
    args = parser.parse_args(args)
    if args.visualize:
        visualizeKCoreDecomposition(getDateObject(args.date))
    else:
        print(dumps(kCoreDecompositionFromDate(datetime.datetime.strptime(args.date, "%Y-%m-%d").date()), indent=2))

if __name__ == "__main__":
    main()