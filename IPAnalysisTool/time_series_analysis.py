# Time series analysis of the k-core decomposition of the network
# Key metrics:
# number of vertices
# number of edges
# average degree
# network diameter
# K-core:
# - individual k-core sizes
# - maximum k-core size
import numpy as np
import pandas as pd
from typing import TypedDict, Optional


class TimeSeriesAnalysisEntry(TypedDict):
    i: int
    network_diameter_ms: Optional[float]
    network_diameter: Optional[int]
    num_vertices: Optional[int]
    num_edges: Optional[int]
    radius_ms: Optional[float]
    max_k_core: Optional[int]
    max_k_core_size: Optional[int]
    k_core: np.ndarray


def process_date(i, date, verbose=False, week_long=False, weighted_edges=False) -> TimeSeriesAnalysisEntry:
    """
    Process a single date for the time series analysis.
    :param i: Index of the week.
    :param date: Date of the week to process. It should point to monday of the given week.
    :param verbose: Verbose output on stdout.
    :param week_long: If true, disregard the week if there is not data for every day of the week.
    :param weighted_edges: Whether to use graphs with weighted edges. This will add additional data to the output, such as weighted diameter, but the accuracy is questionable given the much lower amount of the data.
    :return: A tuple containing the index of the week, the diameter of the network, the number of vertices, the number of edges, the radius of the network, and the sizes of the k-cores.
    """
    from .util.graph_getter import get_graph_by_date
    from .util.calculations import calculate_diameter
    from .util.week_util import get_date_string
    from .k_core import k_core_decomposition
    from json import loads

    try:
        current_graph = get_graph_by_date(date, weighted_edges=weighted_edges)
    except KeyError:
        return TimeSeriesAnalysisEntry(
        i=i,
        network_diameter_ms=None,
        network_diameter=None,
        num_vertices=None,
        num_edges=None,
        radius_ms=None,
        k_core=np.zeros(31, dtype=int),
        max_k_core=None,
        max_k_core_size=None
        )
    k_core_data = k_core_decomposition(current_graph)

    if current_graph:
        # Check if the graph contains data from every day of the week if weekLong is True
        if week_long and len(loads(current_graph.gp.metadata)["route_dates"]) < 7:
            return TimeSeriesAnalysisEntry(
            i=i,
            network_diameter_ms=None,
            network_diameter=None,
            num_vertices=None,
            num_edges=None,
            radius_ms=None,
            k_core=np.zeros(31, dtype=int),
            max_k_core=None,
            max_k_core_size=None
            )
        if weighted_edges:
            diameter = calculate_diameter(current_graph, current_graph.gp.min_weight)
        else:
            diameter = 0
        diameter_vertices = calculate_diameter(current_graph)
        radius = max([current_graph.vp.min_distance[v] for v in current_graph.vertices()])

        # Count vertices and edges
        vertices = current_graph.num_vertices()
        edges = current_graph.num_edges()

        # Process k-cores
        local_k_core_sizes = np.zeros(31, dtype=int)
        for v in current_graph.vertices():
            k = k_core_data["k_core_decomposition"][v]
            local_k_core_sizes[k] += 1
        max_k_core = k_core_data["max_k"]
        max_k_core_size = int(local_k_core_sizes[max_k_core])

        if verbose:
            print("Week " + get_date_string(date) + " done")

        return TimeSeriesAnalysisEntry(
            i=i,
            network_diameter_ms=diameter,
           network_diameter=int(diameter_vertices),
           num_vertices=vertices,
           num_edges=edges,
           radius_ms=radius,
           k_core=local_k_core_sizes,
            max_k_core=max_k_core,
            max_k_core_size=max_k_core_size,
        )
    else:
        return TimeSeriesAnalysisEntry(
            i=i,
            network_diameter_ms=None,
            network_diameter=None,
            num_vertices=None,
            num_edges=None,
            radius_ms=None,
            k_core=np.zeros(31, dtype=int),
            max_k_core=None,
            max_k_core_size=None
        )


def time_series_analysis(verbose=False, date_range=None, max_threads=1, week_long=False, weighted_edges=False):
    from .util.week_util import get_week_dates, get_date_string, get_date_object, get_cache_date_range
    import concurrent.futures
    from functools import partial

    graph_date_range = get_cache_date_range()
    dates = [date[0] for date in get_week_dates(graph_date_range[0], graph_date_range[1])]
    if date_range:
        date_range = [get_date_object(date) for date in date_range]
        earliest_date = max(min(dates), date_range[0])
        latest_date = min(max(dates), date_range[1])
    else:
        earliest_date = min(dates)
        latest_date = max(dates)
    if earliest_date > latest_date:
        return None

    all_dates = [date[0] for date in get_week_dates(earliest_date, latest_date)]
    all_dates_count = len(all_dates)
    if verbose: print(f"Processing {all_dates_count} dates")

    # Initialize data arrays
    network_diameters_in_ms = np.zeros(all_dates_count, dtype=float)
    network_diameters_in_vertices = np.zeros(all_dates_count, dtype=int)
    num_vertices = np.zeros(all_dates_count, dtype=int)
    num_edges = np.zeros(all_dates_count, dtype=int)
    radius = np.zeros(all_dates_count, dtype=float)
    k_core_sizes = np.zeros((all_dates_count, 31), dtype=int)
    max_k_cores = np.zeros(all_dates_count, dtype=int)
    max_k_core_sizes = np.zeros((all_dates_count, 31), dtype=int)

    # Use ProcessPoolExecutor to process dates in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_threads) as executor:
        # Create a partial function with some fixed parameters
        worker = partial(process_date, verbose=verbose, week_long=week_long, weighted_edges=weighted_edges)

        # Submit all tasks and map them to their date index
        future_to_idx = {executor.submit(worker, i, all_dates[i]): i for i in range(all_dates_count)}

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_idx):
            try:
                result = future.result()
                i = result["i"]
                diameter = result["network_diameter_ms"]
                diameter_vertices = result["network_diameter"]
                vertices = result["num_vertices"]
                edges = result["num_edges"]
                current_radius = result["radius_ms"]
                k_core = result["k_core"]
                max_k_core = result["max_k_core"]
                max_k_core_size = result["max_k_core_size"]

                if diameter is not None:
                    network_diameters_in_ms[i] = diameter
                    network_diameters_in_vertices[i] = diameter_vertices
                    num_vertices[i] = vertices
                    num_edges[i] = edges
                    radius[i] = current_radius
                    k_core_sizes[i] = k_core
                    max_k_cores[i] = max_k_core
                    max_k_core_sizes[i] = max_k_core_size

            except Exception as e:
                print(f"Error processing date: {e}")

    date_strings = [get_date_string(date) for date in all_dates]
    data = {
        "date": date_strings,
        "network_diameter_ms": network_diameters_in_ms,
        "network_diameter": network_diameters_in_vertices,
        "num_edges": num_edges,
        "num_vertices": num_vertices,
        "radius_ms": radius,
        "max_k_core": max_k_cores,
        "max_k_core_size": max_k_core_sizes
    }

    # Add k-core columns properly
    for k in range(1, 31):
        data[f"{k}-core"] = [k_core_sizes[i][k] for i in range(all_dates_count)]

    return pd.DataFrame(data)


def main(args=None):
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-o", "--output", help="Choose where to output. The output is a csv file.")
    parser.add_argument("-r", "--range", help="Choose the range of dates to analyze", nargs=2)
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of threads to use. Default is 1. Higher values may result in very high memory usage.")
    parser.add_argument("-l", "--week_long", action="store_true", help="Analyze only full weeks of data.")
    parser.add_argument("-w", "--weighted_edges", action="store_true", help="Use graphs with weighted edges.")
    # Parameters to measure
    parser.add_argument("-a", "--all", action="store_true", help="Analyze all parameters")
    if args == None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)
    print(args.range)
    result = time_series_analysis(args.verbose, args.range, args.threads, args.week_long, args.weighted_edges)
    result.to_csv(args.output, index=False)
    if args.verbose:
        print(f"Data saved to {args.output}")


if __name__ == '__main__':
    main()
