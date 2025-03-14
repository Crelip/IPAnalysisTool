# Time series analysis of the k-core decomposition of the network
# Key metrics:
# number of vertices
# number of edges
# average degree
# biscection width
# network diameter
# K-core:
    # - individual k-core sizes
    # - maximum k-core size
from anyio import current_effective_deadline

from util.weekUtil import getWeekDates, getDateString, getDateObject, getCacheDateRange
from kcore import kCoreDecompositionFromDate
import graph_tool.all as gt
import numpy as np
import pandas as pd
from sortedcontainers import SortedSet
import concurrent.futures
from functools import partial
from json import loads


# Calculate network diameter in parallel
def calculateWeightedDiameter(graph):
    shortest_distances = gt.shortest_distance(graph, weights=graph.ep.minWeight, directed=False)
    return SortedSet(max(shortest_distances[v]) for v in graph.vertices())[-1]


def calculateUnweightedDiameter(graph):
    shortest_distances = gt.shortest_distance(graph, directed=False)
    return SortedSet(max(shortest_distances[v]) for v in graph.vertices())[-1]

def processDate(i, date, verbose = False, weekLong = False, weighted = False):
    try:
        currentGraph, currentKcore, _ = kCoreDecompositionFromDate(date, weighted=weighted, output="graph")
    except KeyError:
        return i, None, None, None, None, None, np.zeros(31, dtype=int)

    if currentGraph:
        # Check if the graph contains data from every day of the week if weekLong is True
        if weekLong and len(loads(currentGraph.gp.metadata)["routeDates"]) < 7:
            return i, None, None, None, None, None, np.zeros(31, dtype=int)
        if weighted: diameter = calculateWeightedDiameter(currentGraph)
        else: diameter = 0
        diameterVertices = calculateUnweightedDiameter(currentGraph)
        radius = max([currentGraph.vp.minDistance[v] for v in currentGraph.vertices()])

        # Count vertices and edges
        vertices = currentGraph.num_vertices()
        edges = currentGraph.num_edges()

        # Process k-cores
        localKcoreSizes = np.zeros(31, dtype=int)
        for v in currentGraph.vertices():
            k = currentKcore[v]
            localKcoreSizes[k] += 1

        if verbose:
            print("Week " + getDateString(date) + " done")
            print(diameter)

        return i, diameter, diameterVertices, vertices, edges, radius, localKcoreSizes
    else:
        return i, 0, 0, 0, 0, 0, np.zeros(31, dtype=int),


def timeSeriesAnalysis(verbose=False, dateRange=None, maxThreads=1, weekLong=False, weighted=False):
    graphDateRange = getCacheDateRange()
    dates = [date[0] for date in getWeekDates(graphDateRange[0], graphDateRange[1])]
    if dateRange:
        dateRange = [getDateObject(date) for date in dateRange]
        earliestDate = max(min(dates), dateRange[0])
        latestDate = min(max(dates), dateRange[1])
    else:
        earliestDate = min(dates)
        latestDate = max(dates)
    if earliestDate > latestDate:
        return None

    allDates = [date[0] for date in getWeekDates(earliestDate, latestDate)]
    allDatesCount = len(allDates)
    print(f"Processing {allDatesCount} dates")

    # Initialize data arrays
    networkDiametersInMs = np.zeros(allDatesCount, dtype=float)
    networkDiametersInVertices = np.zeros(allDatesCount, dtype=int)
    numVertices = np.zeros(allDatesCount, dtype=int)
    numEdges = np.zeros(allDatesCount, dtype=int)
    radius = np.zeros(allDatesCount, dtype=float)
    kCoreSizes = np.zeros((allDatesCount, 31), dtype=int)

    # Use ProcessPoolExecutor to process dates in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=maxThreads) as executor:
        # Create a partial function with some fixed parameters
        worker = partial(processDate, verbose=verbose, weekLong=weekLong, weighted=weighted)

        # Submit all tasks and map them to their date index
        future_to_idx = {executor.submit(worker, i, allDates[i]): i for i in range(allDatesCount)}

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_idx):
            try:
                i, diameter, diameterVertices, vertices, edges, currentRadius, k_cores = future.result()
                if diameter is not None:
                    networkDiametersInMs[i] = diameter
                    networkDiametersInVertices[i] = diameterVertices
                    numVertices[i] = vertices
                    numEdges[i] = edges
                    radius[i] = currentRadius
                    kCoreSizes[i] = k_cores
            except Exception as e:
                print(f"Error processing date: {e}")

    dateStrings = [getDateString(date) for date in allDates]
    data = {
        "date": dateStrings,
        "networkDiameter (ms)": networkDiametersInMs,
        "networkDiameter (vertices)": networkDiametersInVertices,
        "numEdges": numEdges,
        "numVertices": numVertices,
        "radius (ms)": radius
    }

    # Add k-core columns properly
    for k in range(1, 31):
        data[f"{k}-core"] = [kCoreSizes[i][k] for i in range(allDatesCount)]

    return pd.DataFrame(data)

def main(args = None):
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-o", "--output", help="Choose where to output")
    parser.add_argument("-r", "--range", help="Choose the range of dates to analyze", nargs=2)
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of threads")
    parser.add_argument("-l", "--weekLong", action="store_true", help="Analyze only full weeks of data.")
    parser.add_argument("-w", "--weighted", action="store_true", help="Use edge weights")
    # Parameters to measure
    parser.add_argument("-a", "--all", action="store_true", help="Analyze all parameters")
    if args == None: args = parser.parse_args()
    else: args = parser.parse_args(args)
    print(args.range)
    result = timeSeriesAnalysis(args.verbose, args.range, args.threads, args.weekLong, args.weighted)
    result.to_csv(args.output, index=False)
    if args.verbose:
        print(f"Data saved to {args.output}")

if __name__ == '__main__':
    main()