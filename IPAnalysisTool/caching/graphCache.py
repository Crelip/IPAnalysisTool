# Script for collecting graph data over weeks and turning it into graphs
# Splits data weekly
# By default, the script goes through all weeks for which a record does exist.
# -i [YYYY-MM-DD] [YYYY-MM-DD]: Generates a graph only for the list of weeks which begin with the week containing the first given date and ends with the week containing the second given date.
# -t [YYYY-MM-DD]: Generates a graph only for the aforementioned weeks which include the given date.

## These arguments are not implemented yet
# -o [folder]: Outputs the data to the given folder. By default the program outputs data to $HOME/.cache/IPAnalysisTool/graphs/
# -e: If this flag is given, the program does not overwrite existing data.
# -c [filename]: Uses a custom config file. Default config file: $HOME/.config/IPAnalysisTool/config.conf 

from datetime import datetime, timedelta
import os
from graph_tool import Graph
from typing import Tuple
from ..util.weekUtil import getWeek, getWeekDates, getDateString
from ..util.whoisUtil import WhoIs
from ..util.databaseUtil import connectToRemoteDB
from json import dumps
from sortedcontainers import SortedSet

def is_nondecreasing_array(arr):
    size = len(arr)
    for i in range(1, size):
        if arr[i] < arr[i - 1]:
            return False
    return True

# Gets the earliest and latest date in the database
def get_database_range() -> Tuple[datetime.date, datetime.date]:
    # Database connection setup
    rem_conn, rem_cur = connectToRemoteDB()

    # Get the earliest date
    rem_cur.execute("SELECT MIN(t_date) FROM topology")
    record = rem_cur.fetchone()
    earliest_date = record[0]

    # Get the latest date
    rem_cur.execute("SELECT MAX(t_date) FROM topology")
    record = rem_cur.fetchone()
    latest_date = record[0]

    rem_cur.close()
    rem_conn.close()

    return earliest_date, latest_date

# Generates a graph based on all data from start date to end date
def generate_interval_data(start, end, rem_cur, data_folder : str, verbose : bool, weighted_edges : bool = False, collect_metadata : bool = False):

    # Adding a node to the graph
    def add_node(g, address, times, i, endpoint):
        if address not in address_to_vertex:
            node = g.add_vertex()
            address_to_vertex[address] = node
            vertex_to_address[node] = address
            ip_address[node] = address
            min_node_distance[node] = times[i]
            max_node_distance[node] = times[i]
            if collect_metadata: node_properties[node] = who.lookup(address)
        else:
            node = address_to_vertex[address]
            if times[i] < min_node_distance[node]: min_node_distance[node] = times[i]
            if times[i] > max_node_distance[node]: max_node_distance[node] = times[i]
        if address == endpoint:
            position_in_route[node] = 2
        return node

    start = datetime.strftime(start, '%Y-%m-%d')
    end = datetime.strftime(end, '%Y-%m-%d')

    g = Graph(directed=True)
    traversals_num = g.new_edge_property("int")
    ip_address = g.new_vertex_property("string")
    position_in_route = g.new_vertex_property("int") # 1 - start, 2 - end
    node_distances = g.new_vertex_property("vector<double>")
    min_node_distance = g.new_vertex_property("float")
    max_node_distance = g.new_vertex_property("float")
    avg_node_distance = g.new_vertex_property("float")
    node_properties = g.new_vertex_property("string")

    g.edge_properties['traversals'] = traversals_num
    g.vertex_properties['ip'] = ip_address
    g.vertex_properties['positionInRoute'] = position_in_route
    g.vertex_properties['nodeDistances'] = node_distances
    g.vertex_properties['minDistance'] = min_node_distance
    g.vertex_properties['maxDistance'] = max_node_distance
    g.vertex_properties['avgDistance'] = avg_node_distance
    g.vertex_properties['properties'] = node_properties

    g.vp["routes"] = g.new_vertex_property("vector<int>")
    g.ep["routes"] = g.new_edge_property("vector<int>")

    who = WhoIs()
    address_to_vertex = {}
    vertex_to_address = {}

    if weighted_edges:
        edge_weights = g.new_edge_property("vector<double>")
        min_edge_weight = g.new_edge_property("float")
        avg_edge_weight = g.new_edge_property("float")
        max_edge_weight = g.new_edge_property("float")
        g.edge_properties['weights'] = edge_weights
        g.edge_properties['avgWeight'] = avg_edge_weight
        g.edge_properties['maxWeight'] = max_edge_weight
        g.edge_properties['minWeight'] = min_edge_weight

    # Adding starting IP address
    starting_address = "127.0.0.1"
    node = g.add_vertex()
    address_to_vertex[starting_address] = node
    vertex_to_address[node] = starting_address
    ip_address[node] = starting_address
    position_in_route[node] = 1
    node_distances[node] = [0]

    rem_cur.execute(f"""
                    SELECT t_route, t_roundtrip, t_date FROM topology t JOIN non_reserved_ip n ON n.ip_addr = t.ip_addr
                       WHERE NOT ('0.0.0.0/32' = ANY(t_route))
                       AND t_status = 'C'
                       AND t_date >= '{start}'
                       AND t_date < '{end}'
                       AND t_hops > 1
""")

    existing_edges = {}
    route_dates = SortedSet()

    for route_index, record in enumerate(rem_cur):
        route = record[0]
        times = record[1]
        if weighted_edges and not is_nondecreasing_array(times): continue
        date = record[2]
        endpoint = route[-1].split("/")[0]
        route_length = len(route)
        g.vp.routes[address_to_vertex["127.0.0.1"]].append(route_index)
        for i in range(route_length):
            if i == 0: src, dest = starting_address, route[i]
            else: src, dest = route[i - 1], route[i]

            if not(src == '0.0.0.0/32' or dest == '0.0.0.0/32') and src != dest:
                src_address = src.split("/")[0]
                dest_address = dest.split("/")[0]

                # If the source address isn't in graph yet, add it
                if(src_address not in address_to_vertex):
                    src_node = add_node(g, src_address, times, i - 1, endpoint)
                    address_to_vertex[src_address] = src_node
                # If the destination address isn't in graph yet, add it
                if(dest_address not in address_to_vertex):
                    dest_node = add_node(g, dest_address, times, i, endpoint)
                    address_to_vertex[dest_address] = dest_node

                # Add edge if it doesn't exist
                if (src_address, dest_address) not in existing_edges.keys():
                    edge = g.add_edge(address_to_vertex[src_address], address_to_vertex[dest_address])
                    existing_edges[(src_address, dest_address)] = edge
                    traversals_num[edge] = 1
                    if weighted_edges:
                        min_edge_weight[edge] = times[i] - (times[i - 1] if i > 0 else 0)
                # Update edge's weights if it does exist
                else:
                    edge = existing_edges[(src_address, dest_address)]
                    # Increment number of traversals
                    traversals_num[edge] += 1

                # Add distance to node
                node_distances[dest_node].append(times[i])

                # Add route index to edge and vertex
                g.ep.routes[edge].append(route_index)
                g.vp.routes[dest_node].append(route_index)

                if weighted_edges:
                    edgeWeight = times[i] - (times[i - 1] if i > 0 else 0)
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

    metadata = g.new_graph_property("string")
    g.gp["metadata"] = metadata
    g.gp["metadata"] = dumps({"date": start,
                              "routeDates": [getDateString(date) for date in route_dates],
                              "weightedEdges": weighted_edges})
    data_folder = data_folder + f"/{'base' if not weighted_edges else 'weighted'}"
    if not os.path.exists(data_folder): os.makedirs(data_folder)
    g.save(f"{data_folder}/{start}.gt")
    if verbose:
        print(f"Generated{' weighted' if weighted_edges else ''} graph for week starting with {start}.")
        print(f"Number of vertices: {g.num_vertices()}\nNumber of edges: {g.num_edges()}")
    who.close()

# For each week, generate a graph using generateOutput()
def generateWeeklyData(start: datetime.date, end: datetime.date, verbose: bool, weightedEdges : bool = False, collectMetadata : bool = False):
    # Database connection setup
    rem_conn, rem_cur = connectToRemoteDB()

    data_folder : str = os.path.expanduser("~/.cache/IPAnalysisTool/graphs/week")
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

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
    if verbose: print("Created non_reserved_ip table.")
    weeks = getWeekDates(start, end)
    for week in weeks:
        generate_interval_data(week[0], week[0] + timedelta(days=7), rem_cur, data_folder, verbose, weightedEdges)

    rem_cur.close()
    rem_conn.close()

def main(args = None):
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-i", "--interval", nargs=2,
                        help="Generates a graph only for the aforementioned time interval which begins with the interval containing the first given date and ends with the interval containing the second given date.")
    parser.add_argument("-t", "--time",
                        help="Generates a graph only for the aforementioned time interval which includes the given date.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-w", "--weightedEdges", action="store_true", help="Use edge weights")
    parser.add_argument("-m", "--metadata", action="store_true", help="Collect information about each IP address from WHOIS. May take a very long time.")

    args = parser.parse_args(args)

    if args.interval:
        start = getWeek(datetime.strptime(args.interval[0], "%Y-%m-%d"))[0]
        end = getWeek(datetime.strptime(args.interval[1], "%Y-%m-%d"))[1]
    elif args.time:
        start, end = getWeek(datetime.strptime(args.time, "%Y-%m-%d"))
    else:
        start, end = get_database_range()

    generateWeeklyData(start, end, args.verbose, args.weightedEdges, args.metadata)

if __name__ == "__main__": main()
