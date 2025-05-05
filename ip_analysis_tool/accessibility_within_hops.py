# How much of the network is accessible within a certain number of hops
import graph_tool.all as gt
from collections import defaultdict
from pandas import DataFrame

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def accessibility_within_hops(g: gt.Graph, get_ip_addresses = False) -> DataFrame:
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
    distance_records = []
    for i in range(max_dist + 1):
        ips = ip_by_distance[i]
        count = len(ips)
        cumulative_count = sum(len(ip_by_distance[j]) for j in range(i + 1))
        record = {
            "distance": i,
            "count": count,
            "percentage": count / g.num_vertices() * 100,
            "cumulative_count": cumulative_count,
            "cumulative_percentage": cumulative_count / g.num_vertices() * 100
        }
        if get_ip_addresses:
            record["IPs"] = ips
        distance_records.append(record)
    return DataFrame(distance_records)

def main():
    from argparse import ArgumentParser
    from util.date_util import get_date_object
    from util.graph_getter import get_graph_by_date
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates a graph for the week containing the given date.")
    parser.add_argument("-o", "--output", help="Output file path.")
    args = parser.parse_args()
    if args.date:
        print(accessibility_within_hops(get_graph_by_date(get_date_object("%Y-%m-%d"))))
    else:
        print("Please provide a date.")
        exit(1)

if __name__ == "__main__":
    main()