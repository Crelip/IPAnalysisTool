# How much of the network is accessible within a certain number of hops
import graph_tool.all as gt
import datetime
import os
from util.weekUtil import getWeek
import json
from collections import defaultdict

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

# Internal function for finding the accessibility within hops
def internalAccessibilityWithinHops(date, doStructuredOutput: bool = False, outputFolder = "."):
    dateStripped = date.strftime('%Y-%m-%d')
    try:
        g : gt.Graph = gt.load_graph(os.path.expanduser(f"~/.cache/IPAnalysisTool/graphs/week/{dateStripped}.gt"))
    except:
        raise FileNotFoundError("Graph file not found.")
    for v in g.vertices():
            if g.vp.positionInRoute[v] == 1:
                startVertex = v
                break
    #BFS
    # Compute the shortest distances from the start vertex to all vertices
    distances = gt.shortest_distance(g, source=g.vertex(startVertex))
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
    IPByDistance = defaultdict(list)
    for v in g.vertices():
        IPByDistance[distances[v]].append(g.vp.ip[v])
    
    # Returning a structured JSON object
    if doStructuredOutput:
        output = {
            "maxHops": max_dist,
            "IPCount": g.num_vertices(),
            "distances": [
                {
                    "distance": i,
                    "count": len(IPByDistance[i]),
                    "percentage": len(IPByDistance[i]) / g.num_vertices() * 100,
                    "cumulativeCount": sum(len(IPByDistance[j]) for j in range(i + 1)),
                    "cumulativePercentage": sum(len(IPByDistance[j]) for j in range(i + 1)) / g.num_vertices() * 100,
                    "IPs": IPByDistance[i]
                } for i in range(max_dist + 1)
            ]
        }
        outputFolderPath = os.path.abspath(os.path.expanduser(outputFolder))
        if not os.path.exists(outputFolderPath):
            os.makedirs(outputFolderPath, exist_ok=True)
        outputFile = os.path.join(outputFolderPath, f"{dateStripped}.json")
        with open(outputFile, "w") as f:
            f.write(json.dumps(output, indent=2))


# Interface for other scripts
def accessibilityWithinHops(date: datetime.date, doStructuredOutput: bool = False):
    date = getWeek(date)[0]
    dateStripped = date.strftime('%Y-%m-%d')
    try:
        internalAccessibilityWithinHops(date, doStructuredOutput)
    # If the data is not found in the cache, generate the data, then try again
    except FileNotFoundError:
        print("Data not found in cache. Generating data...")
        from graphCache import generateWeeklyData
        generateWeeklyData(date, getWeek(date)[1])
        try:
           internalAccessibilityWithinHops(date, doStructuredOutput)
        except:
            print("Data could not be generated.")
            exit(1)

def main():
    from argparse import ArgumentParser
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates a graph for the week containing the given date.")
    parser.add_argument("-s", "--structured", action="store_true", help="Outputs the data in a structured JSON format.")
    args = parser.parse_args()
    if args.date:
        accessibilityWithinHops(datetime.datetime.strptime(args.date, "%Y-%m-%d").date(), args.structured)
    else:
        print("Please provide a date.")
        exit(1)

if __name__ == "__main__":
    main()