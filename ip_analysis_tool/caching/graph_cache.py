from datetime import datetime, timedelta
import os
from graph_tool import Graph
from ..util.date_util import get_parent_interval, iterate_range, get_date_string
from ..util.database_util import connect_to_remote_db
from json import dumps
from sortedcontainers import SortedSet
from ..enums import TimeInterval
import yaml

def is_nondecreasing_array(arr):
    size = len(arr)
    for i in range(1, size):
        if arr[i] < arr[i - 1]:
            return False
    return True

def load_starting_address():
    """
    Loads the starting address from the config file. If the starting address isn't defined, 'localhost' is returned.
    """
    config_folder = os.path.expanduser("~/.config/IPAnalysisTool")
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)
    config = None
    try:
        with open(config_folder + "/config.yml", "r") as f:
            config = yaml.safe_load(f)
    except:
        print("Error loading config file. Please check your login details.")
        return "localhost"

    return config["starting_address"] if config["starting_address"] else "localhost"

# Generates a graph based on all data from start date to end date
def generate_interval_data(start, end, rem_cur, data_folder : str, verbose : bool, weighted_edges : bool = False, time_interval : TimeInterval = TimeInterval.WEEK):

    def add_node(g, address, times, i, endpoint):
        """
        Adds a node to the graph if it doesn't exist, otherwise updates the node's properties.
        """
        if i == -1: return starting_node
        # Check if the address is already in the graph
        if address not in address_to_node:
            node = g.add_vertex()
            address_to_node[address] = node
            node_to_address[node] = address
            ip_address[node] = address
            min_node_distance[node] = times[i] / 2
            max_node_distance[node] = times[i] / 2
            avg_node_distance[node] = times[i] / 2
        else:
            # If the address is already in the graph, only update the node's properties
            node = address_to_node[address]
            avg_node_distance[node] = (avg_node_distance[node] + float(times[i] / 2)) / 2
            if times[i] < min_node_distance[node]: min_node_distance[node] = times[i] / 2
            if times[i] > max_node_distance[node]: max_node_distance[node] = times[i] / 2
        # Add position in route
        if address == endpoint:
            position_in_route[node] = 2
        return node

    start = datetime.strftime(start, '%Y-%m-%d')
    end = datetime.strftime(end, '%Y-%m-%d')

    g = Graph(directed=True)

    # Set up vertex properties
    ip_address = g.new_vertex_property("string")
    position_in_route = g.new_vertex_property("int") # 1 - start, 2 - end
    node_distances = g.new_vertex_property("vector<double>")
    min_node_distance = g.new_vertex_property("float")
    max_node_distance = g.new_vertex_property("float")
    avg_node_distance = g.new_vertex_property("float")
    g.vp["traversals"] = g.new_vertex_property("int")
    g.vp["hop_distance"] = g.new_vertex_property("int")
    g.vp['ip'] = ip_address
    g.vp['position_in_route'] = position_in_route
    g.vp['distances'] = node_distances
    g.vp['min_distance'] = min_node_distance
    g.vp['max_distance'] = max_node_distance
    g.vp['avg_distance'] = avg_node_distance
    g.vp["routes"] = g.new_vertex_property("vector<int>")

    # Set up edge properties
    traversals_num = g.new_edge_property("int")
    g.ep['traversals'] = traversals_num
    g.ep["routes"] = g.new_edge_property("vector<int>")

    address_to_node = {}
    node_to_address = {}

    if weighted_edges:
        edge_weights = g.new_edge_property("vector<double>")
        min_edge_weight = g.new_edge_property("float")
        avg_edge_weight = g.new_edge_property("float")
        max_edge_weight = g.new_edge_property("float")
        g.edge_properties['weights'] = edge_weights
        g.edge_properties['avg_weight'] = avg_edge_weight
        g.edge_properties['max_weight'] = max_edge_weight
        g.edge_properties['min_weight'] = min_edge_weight

    rem_cur.execute(f"""
                    SELECT t_route, t_roundtrip, t_date FROM topology t JOIN non_reserved_ip n ON n.ip_addr = t.ip_addr
                       WHERE NOT ('0.0.0.0/32' = ANY(t_route))
                       AND t_status = 'C'
                       AND t_date >= '{start}'
                       AND t_date <= '{end}'
                       AND t_hops > 1
""")

    existing_edges = {}
    route_dates = SortedSet()
    starting_node = g.add_vertex()
    starting_address = load_starting_address()
    node_to_address[starting_node] = starting_address
    address_to_node[starting_address] = starting_node

    for route_index, record in enumerate(rem_cur):
        route = record[0]
        times = record[1]
        if weighted_edges and not is_nondecreasing_array(times): continue
        date = record[2]
        g.vp["traversals"][starting_node] += 1
        endpoint = route[-1].split("/")[0]
        route_length = len(route)

        for i in range(route_length):
            if i == 0: src, dest = starting_address, route[0]
            else: src, dest = route[i - 1], route[i]

            if not(src == '0.0.0.0/32' or dest == '0.0.0.0/32') and src != dest:
                src_address = src.split("/")[0]
                dest_address = dest.split("/")[0]

                src_node = add_node(g, src_address, times, i - 1, endpoint)
                dest_node = add_node(g, dest_address, times, i, endpoint)

                # Add edge if it doesn't exist
                if (src_address, dest_address) not in existing_edges.keys():
                    edge = g.add_edge(address_to_node[src_address], address_to_node[dest_address])
                    existing_edges[(src_address, dest_address)] = edge
                    traversals_num[edge] = 1
                    if weighted_edges:
                        min_edge_weight[edge] = (times[i] - (times[i - 1] if i > 0 else 0)) / 2
                # Update edge's weights if it does exist
                else:
                    edge = existing_edges[(src_address, dest_address)]


                # Increment number of traversals
                traversals_num[edge] += 1
                g.vp["traversals"][dest_node] += 1
                # Set the hop distance - the smallest we can find
                if (g.vp["hop_distance"][dest_node] == 0 or g.vp["hop_distance"][dest_node] > i + 1) and dest_node != starting_node:
                    g.vp["hop_distance"][dest_node] = i + 1

                # Add distance to node
                node_distances[dest_node].append(times[i] / 2)

                # Add route index to edge and vertex
                g.ep.routes[edge].append(route_index)
                g.vp.routes[dest_node].append(route_index)

                if weighted_edges:
                    edgeWeight = (times[i] - (times[i - 1] if i > 0 else 0)) / 2
                    edge_weights[edge].append(edgeWeight)
                    if edgeWeight > float(max_edge_weight[edge]): max_edge_weight[edge] = edgeWeight
                    if edgeWeight < float(min_edge_weight[edge]): min_edge_weight[edge] = edgeWeight

        # Check if we had the date before
        date = date.date()
        if date not in route_dates:
            route_dates.add(date)

    if weighted_edges:
        for e in g.edges():
            avg_edge_weight[e] = sum(edge_weights[e]) / len(edge_weights[e])

    # Add metadata to the graph
    g.gp["metadata"] = g.new_graph_property("string")
    g.gp["metadata"] = dumps({
        "date": start,
        "route_dates": [get_date_string(date) for date in route_dates],
        "weighted_edges": weighted_edges,
        "time_interval": str(time_interval).lower(),
        "overall_trips": g.vp["traversals"][starting_node] if starting_node != None else 0,
        "avg_endpoint_distance": (sum([g.vp["hop_distance"][v] for v in g.vertices() if position_in_route[v] == 2]) / g.vp["traversals"][starting_node]) if g.vp["traversals"][starting_node] != 0 else 0,
        "avg_endpoint_distance_ms": (sum([max_node_distance[v] for v in g.vertices() if position_in_route[v] == 2]) / g.vp["traversals"][starting_node]) if g.vp["traversals"][starting_node] != 0 else 0,
         })
    data_folder = data_folder + f"/{'base' if not weighted_edges else 'weighted'}"
    if not os.path.exists(data_folder): os.makedirs(data_folder)
    if time_interval == TimeInterval.ALL:
        g.save(f"{data_folder}/all.gt")
    g.save(f"{data_folder}/{start}.gt")
    if verbose:
        print(f"Generated{' weighted' if weighted_edges else ''} graph for the {str(time_interval).lower()} starting with {start}.")
        print(f"Number of vertices: {g.num_vertices()}\nNumber of edges: {g.num_edges()}")

# For each time interval, generate a graph
def generate_data(start: datetime.date, end: datetime.date, verbose: bool = False, weighted_edges : bool = False, time_interval : TimeInterval = TimeInterval.WEEK):
    """
    Generates graphs from database data.
    :param start: Date, from which to start graph generation.
    :param end: Date, at which to end graph generation.
    :param verbose: Verbose output.
    :param weighted_edges: Generate a graph with weighted edges, usually results in a much smaller graph.
    :param time_interval: Interval to split the data into.
    :return:
    """
    # Database connection setup
    rem_conn, rem_cur = connect_to_remote_db()

    data_folder : str = os.path.expanduser(f"~/.cache/IPAnalysisTool/graphs/{str(time_interval).lower()}")
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    if verbose: print("Connected to the database, gathering a list of non-reserved IP addresses.")

    # Create a table of non-reserved IP addresses
    rem_cur.execute("""CREATE TEMPORARY TABLE non_reserved_ip AS
                       (SELECT h.ip_addr AS ip_addr FROM hosts h WHERE
                       NOT (h.ip_addr <<= '0.0.0.0/8' 
                       OR h.ip_addr <<= '0.0.0.0/32' 
                       OR h.ip_addr <<= '10.0.0.0/8' 
                        OR h.ip_addr <<= '100.64.0.0/10'
                        OR h.ip_addr <<= '127.0.0.0/8' 
                        OR h.ip_addr <<= '169.254.0.0/16' 
                        OR h.ip_addr <<= '172.16.0.0/12' 
                        OR h.ip_addr <<= '192.0.2.0/24' 
                        OR h.ip_addr <<= '192.88.99.0/24' 
                       OR h.ip_addr  <<= '192.88.99.2/32' 
                       OR h.ip_addr <<= '192.168.0.0/16' 
                        OR h.ip_addr <<= '192.0.0.0/24' 
                       OR h.ip_addr  <<= '198.18.0.0/15' 
                       OR h.ip_addr  <<= '198.51.100.0/24' 
                       OR h.ip_addr <<= '203.0.113.0/24' 
                       OR h.ip_addr <<= '255.255.255.255/32'
                        ) AND (
                            EXISTS (
                                SELECT *
                                FROM topology t
                                WHERE t.ip_addr = h.ip_addr
                                AND t.t_status = 'C'
                            )
                        )
                    )"""
                   )
    if verbose:
        print("Created non-reserved ip list.")
        print(f"Generating graphs by {str(time_interval).lower()}.")

    from ..util.database_util import get_database_range
    data_start, data_end = get_database_range()
    # If we don't do across all the data, we split it into intervals
    if time_interval != TimeInterval.ALL:
        from ..util.date_util import clamp_range
        # Clamp data range to the database range
        start, end = clamp_range(start, end, data_start, data_end)
        intervals = iterate_range(start, end, time_interval)
        for interval in intervals:
            generate_interval_data(interval[0], interval[1] + timedelta(days=1), rem_cur, data_folder, verbose, weighted_edges, time_interval=time_interval)
    # Else if we want the data from the entire range
    else:
        generate_interval_data(data_start, data_end + timedelta(days=1), rem_cur, data_folder, verbose, weighted_edges, time_interval=time_interval)

    rem_cur.close()
    rem_conn.close()

def main(args = None):
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-r", "--range", nargs=2,
                        help="Generates a graph only for the aforementioned time range which begins with the interval containing the first given date and ends with the interval containing the second given date.")
    parser.add_argument("-t", "--time",
                        help="Generates a graph only for the aforementioned time interval which includes the given date.")
    parser.add_argument("-i", "--interval", default="WEEK",
                        help="""Splits the data among time intervals.
                        POSSIBLE VALUES: WEEK, MONTH, YEAR, ALL, default: WEEK
                        """)
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-w", "--weighted_edges", action="store_true", help="Use edge weights")

    args = parser.parse_args(args)

    time_interval = TimeInterval[args.interval.upper()]
    if args.range and time_interval != TimeInterval.ALL:
        start = get_parent_interval(datetime.strptime(args.range[0], "%Y-%m-%d"), time_interval=time_interval)[0]
        end = get_parent_interval(datetime.strptime(args.range[1], "%Y-%m-%d"), time_interval=time_interval)[1]
    elif args.time and time_interval != TimeInterval.ALL:
        start, end = get_parent_interval(datetime.strptime(args.time, "%Y-%m-%d"), time_interval=time_interval)
    else:
        from ..util.database_util import get_database_range
        start, end = get_database_range()

    generate_data(start, end, args.verbose, args.weighted_edges, time_interval=time_interval)

if __name__ == "__main__": main()
