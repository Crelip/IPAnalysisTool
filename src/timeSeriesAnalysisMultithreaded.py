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

from util.weekUtil import getWeekDates, getDateString, getDateObject, getCacheDateRange
from kcore import kcoreDecomposition
import graph_tool.all as gt
import numpy as np
import pandas as pd
from sortedcontainers import SortedSet
import concurrent.futures
from functools import partial


# Calculate network diameter in parallel
def calculateWeightedDiameter(graph):
    shortest_distances = gt.shortest_distance(graph, weights=graph.ep.minEdge, directed=False)
    return SortedSet(max(shortest_distances[v]) for v in graph.vertices())[-1]


def calculateUnweightedDiameter(graph):
    shortest_distances = gt.shortest_distance(graph, directed=False)
    return SortedSet(max(shortest_distances[v]) for v in graph.vertices())[-1]

def processDate(i, date, verbose=False):
    try:
        currentGraph, currentKcore, _ = kcoreDecomposition(date, output="graph")
    except KeyError:
        return i, None, None, None, None

    if currentGraph:
        # Execute both calculations using separate processes
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            weighted_future = executor.submit(calculateWeightedDiameter, currentGraph)
            unweighted_future = executor.submit(calculateUnweightedDiameter, currentGraph)

            diameter = weighted_future.result()
            diameterVertices = unweighted_future.result()

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

        return i, diameter, diameterVertices, vertices, edges, localKcoreSizes
    else:
        return i, 0, 0, 0, 0, np.zeros(31, dtype=int)


def timeSeriesAnalysis(verbose=False, dateRange=None, maxThreads=1):
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
    kCoreSizes = np.zeros((allDatesCount, 31), dtype=int)

    # Use ProcessPoolExecutor to process dates in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=maxThreads) as executor:
        # Create a partial function with fixed verbose parameter
        worker = partial(processDate, verbose=verbose)

        # Submit all tasks and map them to their date index
        future_to_idx = {executor.submit(worker, i, allDates[i]): i for i in range(allDatesCount)}

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_idx):
            try:
                i, diameter, diameterVertices, vertices, edges, k_cores = future.result()
                if diameter is not None:
                    networkDiametersInMs[i] = diameter
                    networkDiametersInVertices[i] = diameterVertices
                    numVertices[i] = vertices
                    numEdges[i] = edges
                    kCoreSizes[i] = k_cores
            except Exception as e:
                print(f"Error processing date: {e}")

    dateStrings = [getDateString(date) for date in allDates]
    data = {
        "date": dateStrings,
        "networkDiameter (ms)": networkDiametersInMs,
        "networkDiameter (vertices)": networkDiametersInVertices,
        "numEdges": numEdges,
        "numVertices": numVertices
    }

    # Add k-core columns properly
    for k in range(1, 31):
        data[f"{k}-core"] = [kCoreSizes[i][k] for i in range(allDatesCount)]

    return pd.DataFrame(data)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-o", "--output", help="Choose where to output")
    parser.add_argument("-r", "--range", help="Choose the range of dates to analyze", nargs=2)
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of threads")
    # Parameters to measure
    parser.add_argument("-a", "--all", action="store_true", help="Analyze all parameters")
    args = parser.parse_args()
    print(args.range)
    result = timeSeriesAnalysis(args.verbose, args.range, args.threads)
    result.to_csv(args.output, index = False)
    if args.verbose:
        print(f"Data saved to {args.output}")