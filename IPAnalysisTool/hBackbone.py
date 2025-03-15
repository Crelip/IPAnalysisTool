import graph_tool.all as gt
import datetime

from util.graphGetter import getGraphByDate
from util.calculations import getHIndex
from util.graphManipulation import addInverseEP
from visualize import baseVisualize


# Get bridge of the network
def addBridge(g: gt.Graph, modifier):
    inverse = g.new_edge_property("float")
    g.edge_properties["minEdgeInverse"] = inverse
    bridge = g.new_edge_property("double")
    g.edge_properties["bridge"] = bridge
    for e in g.edges():
        inverse[e] = 1 / g.ep.minEdge[e]
    vertexBetweenness, edgeBetweenness = gt.betweenness(g)
    edgeBetweenness = {e: edgeBetweenness[e] for e in g.edges()}
    # print(g.num_vertices())
    # print(g.num_edges())
    # print(max([edgeBetweenness[e] for e in g.edges()]))

    vertexAmount = g.num_vertices()
    # Modified bridge measurement
    for e in g.edges():
        bridge[e] = edgeBetweenness[e] / vertexAmount * modifier
    return g
    # Bridge measurement
    # return {e: edgeBetweenness[e] / vertexAmount for e in g.edges()}


# Get H-Bridge of the network
def getHBridge(g: gt.Graph, bridge=None) -> int:
    if bridge == None: bridge = addBridge(g).ep.bridge
    # H-Bridge calculation using h-index algorithm
    return getHIndex(g, bridge, count=g.num_edges())


def getHStrength(g: gt.Graph, inv) -> int:
    # H-strength calculation using h-index algorithm
    return getHIndex(g, inv, count=g.num_edges())


# Get H-Backbone of the network
def hBackbone(date: datetime.date, **kwargs):
    modifier = kwargs.get("modifier") or 1000000000
    print(modifier)
    visualize = kwargs.get("visualize", False)
    g: gt.Graph = getGraphByDate(date)
    g = addInverseEP(g)
    g = addBridge(g, modifier)
    bridge = g.ep.bridge
    # for e in g.edges(): print(bridge[e])
    # H-Bridge calculation
    HStrengthProperty = g.ep.traversals
    HBridge: int = getHBridge(g, bridge)
    HStrength: int = getHStrength(g, HStrengthProperty)
    hEdges = set()
    # print(HBridge)
    # print(HStrength)
    for e in g.edges():
        if bridge[e] >= HBridge:
            hEdges.add(e)
        if HStrengthProperty[e] >= HStrength:
            hEdges.add(e)

    # Filter out the graph
    efilt = g.new_ep("bool", vals=[False] * g.num_edges())
    for e in hEdges:
        efilt[e] = True
    vfilt = g.new_vp("bool", vals=[False] * g.num_vertices())
    for v in g.vertices():
        vfilt[v] = any([efilt[e] for e in v.all_edges()])
    hBackbone = gt.GraphView(g, vfilt=vfilt, efilt=efilt)

    # Visualize the graph
    if visualize: baseVisualize(hBackbone, f"{datetime.datetime.strftime(date, "%Y-%m-%d")}-h")
    output = kwargs.get("output", "json")
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
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    parser.add_argument("-v", "--visualize", action="store_true", help="Visualizes the graph.")
    parser.add_argument("-m", "--modifier", type=int, help="Modifier for the bridge calculation.")
    args = parser.parse_args()
    hBackbone(datetime.datetime.strptime(args.date, "%Y-%m-%d").date(), modifier=args.modifier, visualize=args.visualize)
    # print(dumps(hBackbone(datetime.datetime.strptime(args.date, "%Y-%m-%d").date(), modifier=args.modifier, visualize=args.visualize), indent=2))
