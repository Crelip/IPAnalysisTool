from graph_tool import Graph
from .util.calculations import getHIndex
from .visualize import baseVisualize

# Get bridge of the network
def addBridge(g: Graph, modifier = 1):
    from graph_tool.all import betweenness
    bridge = g.new_edge_property("double")
    g.edge_properties["bridge"] = bridge
    _, edge_betweenness = betweenness(g)
    edge_betweenness = {e: edge_betweenness[e] for e in g.edges()}
    # print(g.num_vertices())
    # print(g.num_edges())
    # print(max([edgeBetweenness[e] for e in g.edges()]))

    num_vertices = g.num_vertices()
    # Modified bridge measurement
    for e in g.edges():
        bridge[e] = (edge_betweenness[e] / num_vertices) * modifier
    return g

# Get H-Backbone of the network
def h_backbone(g: Graph,
               modifier = 1,
               visualize = False,
               output = "json",
               verbose = False):
    from graph_tool import GraphView
    from json import loads
    date = loads(g.gp.metadata)["date"]
    g = GraphView(g, directed=False)
    g = addBridge(g, modifier)
    bridge = g.ep.bridge
    # H-Bridge calculation
    h_strength_property = g.ep.traversals
    h_bridge: int = getHIndex(g, bridge)
    h_strength: int = getHIndex(g, h_strength_property)
    h_edges = set()
    efilt = g.new_ep("bool", vals=[False] * g.num_edges())
    if verbose:
        print("HBridge: ", h_bridge)
        print("Hstrength: ", h_strength)
    for e in g.edges(): efilt[e] = ((bridge[e] >= h_bridge) or (h_strength_property[e] >= h_strength))
    vfilt = g.new_vp("bool", vals=[False] * g.num_vertices())
    for v in g.vertices():
        vfilt[v] = any([efilt[e] for e in v.all_edges()])
    h_backbone = GraphView(g, vfilt=vfilt, efilt=efilt)

    # Visualize the graph
    if visualize: baseVisualize(h_backbone, f"{date}-h")
    return {
        "date": date,
        "HBridge": h_bridge,
        "HStrength": h_strength,
        "edgeCount": len(h_edges),
        "count": h_backbone.num_vertices(),
        "IPs": [g.vp.ip[v] for v in h_backbone.vertices()]
    } if output == "json" \
        else h_backbone \
        if output == "graph" \
        else None

def main(args = None):
    from argparse import ArgumentParser
    from .util.graphGetter import getGraphByDate
    from .util.weekUtil import getDateObject
    from json import dumps

    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    parser.add_argument("-s", "--visualize", action="store_true", help="Visualizes the graph.")
    parser.add_argument("-m", "--modifier", type=int, help="Modifier for the bridge calculation.")
    parser.add_argument("-w", "--weightedEdges", action="store_true", help="Use graph with weighted edges.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Prints the output.")

    args = parser.parse_args(args)

    modifier = args.modifier or 1
    h_backbone(getGraphByDate(getDateObject(args.date), args.weightedEdges), modifier=modifier, visualize=args.visualize, verbose=args.verbose)
    # print(dumps(hBackbone(datetime.datetime.strptime(args.date, "%Y-%m-%d").date(), modifier=args.modifier, visualize=args.visualize), indent=2))


if __name__ == "__main__":
    main()