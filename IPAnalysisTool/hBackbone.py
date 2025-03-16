import graph_tool.all as gt
import datetime

from .util.graphGetter import getGraphByDate
from .util.calculations import getHIndex
from .visualize import baseVisualize

# Get bridge of the network
def addBridge(g: gt.Graph, modifier = 1):
    bridge = g.new_edge_property("double")
    g.edge_properties["bridge"] = bridge
    vertexBetweenness, edgeBetweenness = gt.betweenness(g)
    edgeBetweenness = {e: edgeBetweenness[e] for e in g.edges()}
    # print(g.num_vertices())
    # print(g.num_edges())
    # print(max([edgeBetweenness[e] for e in g.edges()]))

    vertexAmount = g.num_vertices()
    # Modified bridge measurement
    for e in g.edges():
        bridge[e] = (edgeBetweenness[e] / vertexAmount) * modifier
    return g

# Get H-Backbone of the network
def hBackbone(date: datetime.date,
              modifier = 1,
              visualize = False,
              weighted = False,
              output = "json",
              verbose = False):

    g: gt.Graph = getGraphByDate(date, weightedEdges=weighted)
    g = gt.GraphView(g, directed=False)
    g = addBridge(g, modifier)
    bridge = g.ep.bridge
    # H-Bridge calculation
    HStrengthProperty = g.ep.traversals
    HBridge: int = getHIndex(g, bridge)
    HStrength: int = getHIndex(g, HStrengthProperty)
    hEdges = set()
    efilt = g.new_ep("bool", vals=[False] * g.num_edges())
    if verbose:
        print("HBridge: ", HBridge)
        print("Hstrength: ", HStrength)
    for e in g.edges(): efilt[e] = ((bridge[e] >= HBridge) or (HStrengthProperty[e] >= HStrength))
    vfilt = g.new_vp("bool", vals=[False] * g.num_vertices())
    for v in g.vertices():
        vfilt[v] = any([efilt[e] for e in v.all_edges()])
    hBackbone = gt.GraphView(g, vfilt=vfilt, efilt=efilt)

    # Visualize the graph
    if visualize: baseVisualize(hBackbone, f"{datetime.datetime.strftime(date, "%Y-%m-%d")}-h")
    return {
        "date": datetime.datetime.strftime(date, "%Y-%m-%d"),
        "HBridge": HBridge,
        "HStrength": HStrength,
        "edgeCount": len(hEdges),
        "count": hBackbone.num_vertices(),
        "IPs": [g.vp.ip[v] for v in hBackbone.vertices()]
    } if output == "json" \
        else hBackbone \
        if output == "graph" \
        else None


if __name__ == "__main__":
    from argparse import ArgumentParser
    from json import dumps

    parser = ArgumentParser()
    import sys
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    parser.add_argument("-s", "--visualize", action="store_true", help="Visualizes the graph.")
    parser.add_argument("-m", "--modifier", type=int, help="Modifier for the bridge calculation.")
    parser.add_argument("-w", "--weightedEdges", action="store_true", help="Use graph with weighted edges.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Prints the output.")
    args = parser.parse_args()
    modifier = args.modifier or 1
    hBackbone(datetime.datetime.strptime(args.date, "%Y-%m-%d").date(), modifier=modifier, visualize=args.visualize, weighted=args.weightedEdges, verbose=args.verbose)
    # print(dumps(hBackbone(datetime.datetime.strptime(args.date, "%Y-%m-%d").date(), modifier=args.modifier, visualize=args.visualize), indent=2))
