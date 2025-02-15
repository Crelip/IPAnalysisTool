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
import psycopg2
import os
import graph_tool.all as gt
from typing import Tuple
from util.weekUtil import getWeek, getWeekDates

# Load environment variables
load_dotenv()

# Gets the earliest and latest date in the database
def getDatabaseRange() -> Tuple[datetime.date, datetime.date]:
    # Database connection setup
    remConn = psycopg2.connect("dbname=" + os.environ["RP_DBNAME"] + " user=" + os.environ["RP_USER"] + " password=" + os.environ["RP_PASSWORD"] + " host=" + os.environ["RP_HOST"])
    remCur = remConn.cursor()

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
def generateIntervalData(start, end, remCur, dataFolder : str):
    start = datetime.strftime(start, '%Y-%m-%d')
    end = datetime.strftime(end, '%Y-%m-%d')

    g = gt.Graph(directed=True)
    minEdgeWeight = g.new_edge_property("float")
    avgEdgeWeight = g.new_edge_property("float")
    ipAddress = g.new_vertex_property("string")
    positionInRoute = g.new_vertex_property("int") # 1 - start, 2 - end

    g.edge_properties['minEdge'] = minEdgeWeight
    g.edge_properties['avgEdge'] = avgEdgeWeight
    g.vertex_properties['ip'] = ipAddress
    g.vertex_properties['positionInRoute'] = positionInRoute
    addressToVertex = {}
    VertexToAddress = {}

    # Adding starting IP address
    remCur.execute(f"""WITH counts AS (SELECT t_route[1] AS address, COUNT(*) AS count FROM topology
                   WHERE NOT (-1 = ANY(t_roundtrip))
                   AND t_date >= '{start}'
                   AND t_date < '{end}'
                   AND t_hops > 1
                   GROUP BY t_route[1])
                   SELECT address 
                   FROM counts ORDER BY count DESC LIMIT 1;""")
    record = remCur.fetchone()
    if(record is None): return
    startingaddress = record[0]
    startingaddress = startingaddress.split("/")[0]
    node = g.add_vertex()
    addressToVertex[startingaddress] = node
    VertexToAddress[node] = startingaddress
    ipAddress[node] = startingaddress
    positionInRoute[node] = 1

    remCur.execute(f"""SELECT t_route, t_roundtrip FROM topology
                   WHERE NOT (-1 = ANY(t_roundtrip))
                   AND NOT ('0.0.0.0/32' = ANY(t_route))
                   AND t_status = 'C'
                   AND t_date >= '{start}'
                   AND t_date <= '{end}'
                   AND t_hops > 1""")

    existingEdges = {}

    for record in remCur:
        route = record[0]
        times = record[1]
        endpoint = route[-1].split("/")[0]
        for i in range(len(route) - 1):
            src, dest = route[i], route[i + 1]
            if not(src == '0.0.0.0/32' or dest == '0.0.0.0/32') and src != dest:
                srcAddress = src.split("/")[0]
                destAddress = dest.split("/")[0]

                if(srcAddress not in addressToVertex):
                    srcNode = g.add_vertex()
                    addressToVertex[srcAddress] = srcNode
                    VertexToAddress[srcNode] = srcAddress
                    ipAddress[srcNode] = srcAddress
                else:
                    srcNode = addressToVertex[srcAddress]

                if(destAddress not in addressToVertex):
                    destNode = g.add_vertex()
                    addressToVertex[destAddress] = destNode
                    VertexToAddress[destNode] = destAddress
                    ipAddress[destNode] = destAddress
                else:
                    destNode = addressToVertex[destAddress]

                # Add edge if it doesn't exist
                if (srcAddress, destAddress) not in existingEdges.keys():
                    edge = g.add_edge(addressToVertex[srcAddress], addressToVertex[destAddress])
                    existingEdges[(srcAddress, destAddress)] = edge
                    minEdgeWeight[edge] = times[i]
                    avgEdgeWeight[edge] = times[i]
                # Update edge's weights if it does exist
                else:
                    edge = existingEdges[(srcAddress, destAddress)]
                    # Average ping between 2 points
                    avgEdgeWeight[edge] = (avgEdgeWeight[edge] + float(times[i])) / 2
                    # Shortest ping between 2 points
                    if minEdgeWeight[edge] > float(times[i]): minEdgeWeight[edge] = float(times[i])
                
                if destAddress == endpoint:
                    positionInRoute[destNode] = 2

    g.save(f"{dataFolder}/{start}.gt")

# For each week, generate a graph using generateOutput()
def generateWeeklyData(start: datetime.date, end: datetime.date):
    # Database connection setup
    remConn = psycopg2.connect("dbname=" + os.environ["IP_DBNAME"] + " user=" + os.environ["IP_USER"] + " password=" + os.environ["IP_PASSWORD"] + " host=" + os.environ["IP_HOST"])
    remCur = remConn.cursor()

    dataFolder : str = os.path.expanduser("~/.cache/IPAnalysisTool/graphs/week")
    if not os.path.exists(dataFolder):
        os.makedirs(dataFolder)

    weeks = getWeekDates(start, end)
    for week in weeks:
        generateIntervalData(week[0], week[0] + timedelta(days=7), remCur, dataFolder)

    remCur.close()
    remConn.close()

def main():
    from argparse import ArgumentParser
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument("-i", "--interval", nargs=2, help="Generates a graph only for the aforementioned time interval which begins with the interval containing the first given date and ends with the interval containing the second given date.")
    parser.add_argument("-t", "--time", help="Generates a graph only for the aforementioned time interval which includes the given date.")
    args = parser.parse_args()
    if args.interval:
        start = getWeek(datetime.strptime(args.interval[0], "%Y-%m-%d"))[0]
        end = getWeek(datetime.strptime(args.interval[1], "%Y-%m-%d"))[1]
    elif args.time:
        start, end = getWeek(datetime.strptime(args.time, "%Y-%m-%d"))
    else:
        start, end = getDatabaseRange()
    generateWeeklyData(start, end)



if __name__ == "__main__": main()
