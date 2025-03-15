# Script for collecting graph data over weeks and turning it into graphs
# Splits data weekly
# By default, the script goes through all weeks for which a record does exist.
# -i [YYYY-MM-DD] [YYYY-MM-DD]: Generates a graph only for the list of weeks which begin with the week containing the first given date and ends with the week containing the second given date.
# -t [YYYY-MM-DD]: Generates a graph only for the aforementioned weeks which include the given date.

## These arguments are not implemented yet
# -o [folder]: Outputs the data to the given folder. By default the program outputs data to $HOME/.cache/IPAnalysisTool/graphs/
# -e: If this flag is given, the program does not overwrite existing data.
# -c [filename]: Uses a custom config file. Default config file: $HOME/.config/IPAnalysisTool/config.conf 

from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import graph_tool.all as gt
from typing import Tuple
from ..util.weekUtil import getWeek, getWeekDates, getDateString
from ..util.whoisUtil import WhoIs
from ..util.databaseUtil import connectToRemoteDB
from json import dumps
from sortedcontainers import SortedSet

# Load environment variables
load_dotenv(override=True)

def isNondecreasingArray(arr):
    size = len(arr)
    for i in range(1, size):
        if arr[i] < arr[i - 1]:
            return False
    return True

# Gets the earliest and latest date in the database
def getDatabaseRange() -> Tuple[datetime.date, datetime.date]:
    # Database connection setup
    remConn, remCur = connectToRemoteDB()

    # Get the earliest date
    remCur.execute("SELECT MIN(t_date) FROM topology")
    record = remCur.fetchone()
    earliestDate = record[0]

    # Get the latest date
    remCur.execute("SELECT MAX(t_date) FROM topology")
    record = remCur.fetchone()
    latestDate = record[0]

    remCur.close()
    remConn.close()

    return earliestDate, latestDate

# Generates a graph based on all data from start date to end date
def generateIntervalData(start, end, remCur, dataFolder : str, verbose : bool, weightedEdges : bool = False, collectMetadata : bool = False):

    # Adding a node to the graph
    def addNode(g, address, times, i, endpoint):
        if address not in addressToVertex:
            node = g.add_vertex()
            addressToVertex[address] = node
            VertexToAddress[node] = address
            ipAddress[node] = address
            minNodeDistance[node] = times[i]
            maxNodeDistance[node] = times[i]
            if collectMetadata: nodeProperties[node] = who.lookup(address)
        else:
            node = addressToVertex[address]
            if times[i] < minNodeDistance[node]: minNodeDistance[node] = times[i]
            if times[i] > maxNodeDistance[node]: maxNodeDistance[node] = times[i]
        if address == endpoint:
            positionInRoute[node] = 2
        return node

    start = datetime.strftime(start, '%Y-%m-%d')
    end = datetime.strftime(end, '%Y-%m-%d')

    g = gt.Graph(directed=True)
    traversalsNum = g.new_edge_property("int")
    ipAddress = g.new_vertex_property("string")
    positionInRoute = g.new_vertex_property("int") # 1 - start, 2 - end
    nodeDistances = g.new_vertex_property("vector<double>")
    minNodeDistance = g.new_vertex_property("float")
    maxNodeDistance = g.new_vertex_property("float")
    avgNodeDistance = g.new_vertex_property("float")
    nodeProperties = g.new_vertex_property("string")

    g.edge_properties['traversals'] = traversalsNum
    g.vertex_properties['ip'] = ipAddress
    g.vertex_properties['positionInRoute'] = positionInRoute
    g.vertex_properties['nodeDistances'] = nodeDistances
    g.vertex_properties['minDistance'] = minNodeDistance
    g.vertex_properties['maxDistance'] = maxNodeDistance
    g.vertex_properties['avgDistance'] = avgNodeDistance
    g.vertex_properties['properties'] = nodeProperties

    who = WhoIs()
    addressToVertex = {}
    VertexToAddress = {}

    if weightedEdges:
        edgeWeights = g.new_edge_property("vector<double>")
        minEdgeWeight = g.new_edge_property("float")
        avgEdgeWeight = g.new_edge_property("float")
        maxEdgeWeight = g.new_edge_property("float")
        g.edge_properties['weights'] = edgeWeights
        g.edge_properties['avgWeight'] = avgEdgeWeight
        g.edge_properties['maxWeight'] = maxEdgeWeight
        g.edge_properties['minWeight'] = minEdgeWeight

    # Adding starting IP address
    startingaddress = "localhost"
    node = g.add_vertex()
    addressToVertex[startingaddress] = node
    VertexToAddress[node] = startingaddress
    ipAddress[node] = startingaddress
    positionInRoute[node] = 1
    nodeDistances[node] = [0]

    remCur.execute(f"""SELECT t_route, t_roundtrip, t_date FROM topology
                   WHERE NOT ('0.0.0.0/32' = ANY(t_route))
                   AND t_status = 'C'
                   AND t_date >= '{start}'
                   AND t_date < '{end}'
                   AND t_hops > 1""")

    existingEdges = {}
    routeDates = SortedSet()
    for record in remCur:
        route = record[0]
        times = record[1]
        if weightedEdges and not isNondecreasingArray(times): continue
        date = record[2]
        endpoint = route[-1].split("/")[0]
        route_length = len(route)
        for i in range(route_length):
            if i == 0: src, dest = startingaddress, route[i]
            else: src, dest = route[i - 1], route[i]

            if not(src == '0.0.0.0/32' or dest == '0.0.0.0/32') and src != dest:
                srcAddress = src.split("/")[0]
                destAddress = dest.split("/")[0]

                # If the source address isn't in graph yet, add it
                if(srcAddress not in addressToVertex):
                    srcNode = addNode(g, srcAddress, times, i - 1, endpoint)
                    addressToVertex[srcAddress] = srcNode
                # If the destination address isn't in graph yet, add it
                if(destAddress not in addressToVertex):
                    destNode = addNode(g, destAddress, times, i, endpoint)
                    addressToVertex[destAddress] = destNode

                # Add edge if it doesn't exist
                if (srcAddress, destAddress) not in existingEdges.keys():
                    edge = g.add_edge(addressToVertex[srcAddress], addressToVertex[destAddress])
                    existingEdges[(srcAddress, destAddress)] = edge
                    traversalsNum[edge] = 1
                    if weightedEdges:
                        minEdgeWeight[edge] = times[i] - (times[i - 1] if i > 0 else 0)
                # Update edge's weights if it does exist
                else:
                    edge = existingEdges[(srcAddress, destAddress)]
                    # Increment number of traversals
                    traversalsNum[edge] += 1

                # Add distance to node
                nodeDistances[destNode].append(times[i])

                if weightedEdges:
                    edgeWeight = times[i] - (times[i - 1] if i > 0 else 0)
                    edgeWeights[edge].append(edgeWeight)
                    if edgeWeight > float(maxEdgeWeight[edge]): maxEdgeWeight[edge] = edgeWeight
                    if edgeWeight < float(minEdgeWeight[edge]): minEdgeWeight[edge] = edgeWeight

        # Check if we had the date before
        date = date.date()
        if date not in routeDates:
            routeDates.add(date)

    if weightedEdges:
        for e in g.edges():
            avgEdgeWeight[e] = sum(edgeWeights[e]) / len(edgeWeights[e])

    metadata = g.new_graph_property("string")
    g.gp["metadata"] = metadata
    g.gp["metadata"] = dumps({"date": start,
                              "routeDates": [getDateString(date) for date in routeDates],
                              "weightedEdges": weightedEdges})
    dataFolder = dataFolder + f"/{'base' if not weightedEdges else 'weighted'}"
    if not os.path.exists(dataFolder): os.makedirs(dataFolder)
    g.save(f"{dataFolder}/{start}.gt")
    if verbose:
        print(f"Generated{' weighted' if weightedEdges else ''} graph for week starting with {start}.")
        print(f"Number of vertices: {g.num_vertices()}\nNumber of edges: {g.num_edges()}")
    who.close()

# For each week, generate a graph using generateOutput()
def generateWeeklyData(start: datetime.date, end: datetime.date, verbose: bool, weightedEdges : bool = False, collectMetadata : bool = False):
    # Database connection setup
    remConn, remCur = connectToRemoteDB()

    dataFolder : str = os.path.expanduser("~/.cache/IPAnalysisTool/graphs/week")
    if not os.path.exists(dataFolder):
        os.makedirs(dataFolder)

    weeks = getWeekDates(start, end)
    for week in weeks:
        generateIntervalData(week[0], week[0] + timedelta(days=7), remCur, dataFolder, verbose, weightedEdges)

    remCur.close()
    remConn.close()

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
    if args == None: args = parser.parse_args()
    else: args = parser.parse_args(args)

    if args.interval:
        start = getWeek(datetime.strptime(args.interval[0], "%Y-%m-%d"))[0]
        end = getWeek(datetime.strptime(args.interval[1], "%Y-%m-%d"))[1]
    elif args.time:
        start, end = getWeek(datetime.strptime(args.time, "%Y-%m-%d"))
    else:
        start, end = getDatabaseRange()

    generateWeeklyData(start, end, args.verbose, args.weightedEdges, args.metadata)

if __name__ == "__main__": main()
