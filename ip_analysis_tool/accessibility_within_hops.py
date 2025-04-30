# How much of the network is accessible within a certain number of hops
import graph_tool.all as gt
import datetime
import os
from util.week_util import get_week
import json
from collections import defaultdict

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def accessibility_within_hops(g, do_structured_output: bool = False):
    for v in g.vertices():
        if g.vp.position_in_route[v] == 1:
            start_vertex = v
            break
    #BFS
    # Compute the shortest distances from the start vertex to all vertices
    distances = gt.shortest_distance(g, source=g.vertex(start_vertex))
    # Debug begin
    # for v in g.vertices():
    #     print(g.vp.ip[v], distances[v])
    # Debug end
    # Convert the distances into a Python list
    dist_list = list(distances)

    # Filter out unreachable vertices: they will typically have 'inf' distance
    reachable_distances = [d for d in dist_list if d < float('inf')]

    # Determine the maximum number of hops required to reach all reachable vertices
    max_dist = int(max(reachable_distances)) if reachable_distances else 0

    # Group the reachable vertices by distance
    ip_by_distance = defaultdict(list)
    for v in g.vertices():
        ip_by_distance[distances[v]].append(g.vp.ip[v])
    
    # Returning a structured JSON object
    if do_structured_output:
        output = {
            "max_hops": max_dist,
            "address_count": g.num_vertices(),
            "distances": [
                {
                    "distance": i,
                    "count": len(ip_by_distance[i]),
                    "percentage": len(ip_by_distance[i]) / g.num_vertices() * 100,
                    "cumulative_count": sum(len(ip_by_distance[j]) for j in range(i + 1)),
                    "cumulative_percentage": sum(len(ip_by_distance[j]) for j in range(i + 1)) / g.num_vertices() * 100,
                    "IPs": ip_by_distance[i]
                } for i in range(max_dist + 1)
            ]
        }
        return output

def main():
    from argparse import ArgumentParser
    from util.date_util import get_date_object
    from util.graph_getter import get_graph_by_date
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates a graph for the week containing the given date.")
    parser.add_argument("-s", "--structured", action="store_true", help="Outputs the data in a structured JSON format.")
    args = parser.parse_args()
    if args.date:
        print(accessibility_within_hops(get_graph_by_date(get_date_object("%Y-%m-%d")), args.structured))
    else:
        print("Please provide a date.")
        exit(1)

if __name__ == "__main__":
    main()