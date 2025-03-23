import json
import graph_tool.all as gt
import datetime
import argparse

def roads_on_edges(date: datetime.date, edge_start: str, edge_end: str) -> str:
    from .util.graph_getter import get_graph_by_date
    g = get_graph_by_date(date)
    endpoints = []
    endpoints_through_path = []
    # Find the vertices corresponding to the edgeStart and edgeEnd + the start and end points of the route
    for v in g.vertices():
        if g.vp.ip[v] == edge_start:
            start_vertex = v
        if g.vp.ip[v] == edge_end:
            end_vertex = v
        if g.vp.position_in_route[v] == 1:
            startpoint = v
        if g.vp.position_in_route[v] == 2:
            endpoints.append(v)
    e = g.edge(start_vertex, end_vertex)
    if e is None or startpoint is None:
        return None
    # Find the shortest path between the start and end points
    for endpoint in endpoints:
        path = gt.shortest_path(g, source = startpoint, target = endpoint, weights=g.ep.minEdge)
        if e in path[1]:
            endpoints_through_path.append(endpoint)
    result = {
        "edge_start": edge_start,
        "edge_end": edge_end,
        "edge_path_amount" : len(endpoints_through_path),
        "endpoint_path_percentage" : len(endpoints_through_path) / len(endpoints) * 100,
        "startpoint": g.vp.ip[startpoint],
        "endpoints": [g.vp.ip[v] for v in endpoints_through_path]
    }
    return json.dumps(result, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    parser.add_argument("-s", "--edge_start", help="The starting point of the edge.")
    parser.add_argument("-e", "--edge_end", help="The ending point of the edge.")
    args = parser.parse_args()
    print(roads_on_edges(datetime.datetime.strptime(args.date, "%Y-%m-%d").date(), args.edge_start, args.edge_end))

if __name__ == "__main__":
    main()