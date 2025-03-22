import graph_tool.all as gt
from graph_tool import topology
import numpy as np
from sortedcontainers import SortedList
from util.week_util import get_week
import os
from datetime import datetime

# Returns the radius of a graph
# mimimum: if True (default), returns the radius based on the minimum values of edges, otherwise returns the radius based on the average values of edges
def radius(date: datetime.date, average: bool = False) -> int:
    inputFile = os.path.expanduser(f'''~/.cache/IPAnalysisTool/graphs/week/{datetime.strftime(
        get_week(date)[0], "%Y-%m-%d")}.gt''')
    g : gt.Graph = gt.load_graph(str(inputFile))
    eccentricities : SortedList = SortedList()
    edgeWeight = g.ep.avgEdge if average else g.ep.minEdge
    for v in g.vertices():
        distances = topology.shortest_distance(g, source=v, weights=edgeWeight).a
        eccentricities.add(np.max(distances))
    return(np.min(eccentricities))

# Return the radius of a graph in the form of a string on stdout
def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates a graph for the week containing the given date.")
    parser.add_argument("-a", "--average", action="store_true", help="Returns the radius based on the average values of edges.")
    args = parser.parse_args()
    if args.date:
        print(radius(datetime.strptime(args.date, "%Y-%m-%d"),
        args.average))
    else:
        print("Please provide a date.")
        exit(1)

if __name__ == "__main__":
    main()