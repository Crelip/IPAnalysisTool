# How much of the network is accessible within a certain number of hops
import graph_tool.all as gt
from collections import defaultdict
from pandas import DataFrame


def clamp(n, smallest, largest): return max(smallest, min(n, largest))


def accessibility_within_hops(g: gt.Graph,
                              get_ip_addresses=False) -> DataFrame:
    """
    Calculate the accessibility within hops for a given graph.
    :param g: The graph to analyze.
    :param get_ip_addresses: If True, include IP addresses in the output.
    :return:
    """
    starting_node = g.vertex(0)
    dist_dict = gt.shortest_distance(g, source=starting_node, directed=False)

    max_dist = int(max(dist_dict)) if dist_dict else 0

    # Group the reachable vertices by distance
    ip_by_distance = defaultdict(list)
    for v in g.vertices():
        ip_by_distance[dist_dict[v]].append(g.vp.ip[v])
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


def accessibility_within_hops_approx(
        g: gt.Graph,
        get_ip_addresses=False) -> DataFrame:
    """
    Calculate the accessibility within hops for a given graph. This is an approximation of the actual distances where it's simply collecting the recorded distances from the data, therefore it's faster, but sometimes less accurate.
    :param g: The graph to analyze.
    :param get_ip_addresses: If True, include IP addresses in the output.
    :return:
    """
    distances = g.vp["hop_distance"]
    dist_list = list(distances)

    max_dist = int(max(dist_list)) if dist_list else 0

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