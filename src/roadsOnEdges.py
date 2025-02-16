import json
import os
import graph_tool.all as gt
import datetime
import argparse

def roadsOnEdges(date: datetime.date, edgeStart: str, edgeEnd: str) -> str:
    inputFile : str = os.path.expanduser(f'''~/.cache/IPAnalysisTool/graphs/week/{datetime.datetime.strftime(date, "%Y-%m-%d")}.gt''')
    g : gt.Graph = gt.load_graph(inputFile)
    endpoints = []
    endpointsThroughPath = []
    # Find the vertices corresponding to the edgeStart and edgeEnd + the start and end points of the route
    for v in g.vertices():
        if g.vp.ip[v] == edgeStart:
            startVertex = v
        if g.vp.ip[v] == edgeEnd:
            endVertex = v
        if g.vp.positionInRoute[v] == 1:
            startpoint = v
        if g.vp.positionInRoute[v] == 2:
            endpoints.append(v)
    e = g.edge(startVertex, endVertex)
    if e is None or startpoint is None:
        return None
    # Find the shortest path between the start and end points
    for endpoint in endpoints:
        path = gt.shortest_path(g, source = startpoint, target = endpoint, weights=g.ep.minEdge)
        if e in path[1]:
            endpointsThroughPath.append(endpoint)
    result = {
        "edgeStart": edgeStart,
        "edgeEnd": edgeEnd,
        "edgePathAmount" : len(endpointsThroughPath),
        "endpointPathPercentage" : len(endpointsThroughPath) / len(endpoints) * 100,
        "startpoint": g.vp.ip[startpoint],
        "endpoints": [g.vp.ip[v] for v in endpointsThroughPath]
    }
    return json.dumps(result, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    parser.add_argument("-s", "--edgeStart", help="The starting point of the edge.")
    parser.add_argument("-e", "--edgeEnd", help="The ending point of the edge.")
    args = parser.parse_args()
    print(roadsOnEdges(datetime.datetime.strptime(args.date, "%Y-%m-%d").date(), args.edgeStart, args.edgeEnd))

if __name__ == "__main__":
    main()