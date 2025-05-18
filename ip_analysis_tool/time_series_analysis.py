# Time series analysis of the k-core decomposition of the network
# Key metrics:
# number of vertices
# number of edges
# network diameter
# K-core:
# - individual k-core sizes
# - maximum k-core size
import numpy as np
import pandas as pd
from typing import TypedDict, Optional
from .enums import TimeInterval


class TimeSeriesAnalysisEntry(TypedDict):
    i: int
    diameter_ms: Optional[float]
    diameter: Optional[int]
    pseudo_diameter_ms: Optional[float]
    pseudo_diameter: Optional[int]
    num_vertices: Optional[int]
    num_edges: Optional[int]
    radius_ms: Optional[float]
    radius: Optional[int]
    max_k_core: Optional[int]
    max_k_core_size: Optional[int]
    average_endpoint_distance_ms: Optional[float]
    average_endpoint_distance: Optional[int]
    k_core: np.ndarray
    distances: np.ndarray


def process_date(
        i,
        date,
        verbose=False,
        weighted_edges=False,
        time_interval: TimeInterval = TimeInterval.WEEK,
        max_k_core_data: int = 100,
        max_distance_data: int = 65,
        diameter=False
) -> TimeSeriesAnalysisEntry:
    """
    Process a single date for the time series analysis.
    :param i: Index of the interval.
    :param date: Date of the interval to process. It should point to the first day of the given interval.
    :param verbose: Verbose output on stdout.
    :param weighted_edges: Whether to use graphs with weighted edges. This will add additional data to the output, such as weighted diameter, but the accuracy is questionable given the much lower amount of the data.
    :return: A tuple containing the index of the interval, the diameter of the network, the number of vertices, the number of edges, the radius of the network, and the sizes of the k-cores.
    """
    from .util.graph_getter import get_graph_by_date
    from .util.calculations import calculate_diameter
    from .util.date_util import get_date_string
    from .k_core import k_core_decomposition
    from json import loads

    try:
        current_graph = get_graph_by_date(
            date,
            weighted_edges=weighted_edges,
            time_interval=time_interval)
    except KeyError:
        return TimeSeriesAnalysisEntry(
            i=i,
            diameter_ms=None,
            diameter=None,
            num_vertices=None,
            num_edges=None,
            radius_ms=None,
            radius=None,
            k_core=np.zeros(max_k_core_data, dtype=int),
            distances=np.zeros(max_distance_data, dtype=int),
            max_k_core=None,
            max_k_core_size=None,
            average_endpoint_distance=None,
            average_endpoint_distance_ms=None
        )
    k_core_data = k_core_decomposition(current_graph)

    if current_graph:
        # Calculate the diameter
        if diameter:
            if weighted_edges:
                diameter = calculate_diameter(
                    current_graph, current_graph.gp.min_weight)
            else:
                diameter = 0
            diameter_vertices = calculate_diameter(current_graph)
        # If we don't want the diameter, set it to 0
        else:
            diameter = 0
            diameter_vertices = 0

        radius_ms = max([current_graph.vp.min_distance[v]
                        for v in current_graph.vertices()])
        radius = max([current_graph.vp.hop_distance[v]
                     for v in current_graph.vertices()])

        # Count vertices and edges
        vertices = current_graph.num_vertices()
        edges = current_graph.num_edges()

        # Process k-cores and distances
        local_k_core_sizes = np.zeros(max_k_core_data, dtype=int)
        local_distances = np.zeros(max_distance_data, dtype=int)
        for v in current_graph.vertices():
            k = k_core_data["k_core_decomposition"][v]
            local_k_core_sizes[k] += 1
            distance = current_graph.vp.hop_distance[v]
            local_distances[distance] += 1

        max_k_core = k_core_data["max_k"]
        max_k_core_size = int(local_k_core_sizes[max_k_core])

        if verbose:
            print(str(time_interval) + " " + get_date_string(date) + " done")

        return TimeSeriesAnalysisEntry(
            i=i,
            diameter_ms=diameter,
            diameter=int(diameter_vertices),
            num_vertices=vertices,
            num_edges=edges,
            radius_ms=radius_ms,
            radius=radius,
            k_core=local_k_core_sizes,
            distances=local_distances,
            max_k_core=max_k_core,
            max_k_core_size=max_k_core_size,
            average_endpoint_distance=loads(
                current_graph.gp.metadata)["avg_endpoint_distance"],
            average_endpoint_distance_ms=loads(
                current_graph.gp.metadata)["avg_endpoint_distance_ms"])
    return TimeSeriesAnalysisEntry(
        i=i,
        diameter_ms=None,
        diameter=None,
        num_vertices=None,
        num_edges=None,
        radius_ms=None,
        radius=None,
        k_core=np.zeros(max_k_core_data, dtype=int),
        distances=np.zeros(max_distance_data, dtype=int),
        max_k_core=None,
        max_k_core_size=None,
        average_endpoint_distance=None,
        average_endpoint_distance_ms=None
    )


def time_series_analysis(
        verbose=False,
        date_range=None,
        max_threads=1,
        weighted_edges=False,
        time_interval: TimeInterval = TimeInterval.WEEK,
        max_k_core_data: int = 100,
        max_distance_data: int = 65,
        diameter=False
) -> pd.DataFrame:
    """
    Generate metrics from graph data.
    :param verbose: Display verbose output on stdout.
    :param date_range: A range of dates to analyze. The format is YYYY-MM-DD YYYY-MM-DD. If not specified, the whole date range will be used.
    :param max_threads: The maximum number of threads to use for processing. Default is 1. Can be quite memory intensive.
    :param weighted_edges: Whether to use graphs with weighted edges. This will add additional data to the output, such as weighted diameter, but the accuracy is questionable given the much lower amount of the data.
    :param time_interval: Time granularity for data processing.
    :param max_k_core_data: The maximum number of kcore decomposition results to return.
    :param max_distance_data: The maximum number of distance data points to return.
    :param diameter: Whether to calculate diameter metrics. Default is False.
    :return:
    """
    from .util.date_util import iterate_range, get_date_string, get_date_object, get_cache_date_range
    import concurrent.futures
    from functools import partial

    graph_date_range = get_cache_date_range()
    dates = [
        date[0] for date in iterate_range(
            graph_date_range[0],
            graph_date_range[1])]
    if date_range:
        date_range = [get_date_object(date) for date in date_range]
        earliest_date = max(min(dates), date_range[0])
        latest_date = min(max(dates), date_range[1])
    else:
        earliest_date = min(dates)
        latest_date = max(dates)
    if earliest_date > latest_date:
        return None

    all_dates = [
        date[0] for date in iterate_range(
            earliest_date,
            latest_date,
            time_interval)]
    all_dates_count = len(all_dates)
    if verbose:
        print(f"Processing {all_dates_count} dates")

    # Initialize data arrays
    network_diameters_in_ms = np.zeros(all_dates_count, dtype=float)
    network_diameters_in_vertices = np.zeros(all_dates_count, dtype=int)
    num_vertices = np.zeros(all_dates_count, dtype=int)
    num_edges = np.zeros(all_dates_count, dtype=int)
    radii_ms = np.zeros(all_dates_count, dtype=float)
    radii = np.zeros(all_dates_count, dtype=int)
    k_core_sizes = np.zeros((all_dates_count, max_k_core_data), dtype=int)
    distances = np.zeros((all_dates_count, max_distance_data), dtype=int)
    max_k_cores = np.zeros(all_dates_count, dtype=int)
    max_k_core_sizes = np.zeros(all_dates_count, dtype=int)
    avg_endpoint_distances = np.zeros(all_dates_count, dtype=int)
    avg_endpoint_distances_ms = np.zeros(all_dates_count, dtype=float)

    # Use ProcessPoolExecutor to process dates in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_threads) as executor:
        # Create a partial function with some fixed parameters
        worker = partial(
            process_date,
            verbose=verbose,
            weighted_edges=weighted_edges,
            time_interval=time_interval,
            max_k_core_data=max_k_core_data,
            diameter=diameter)

        # Submit all tasks and map them to their date index
        future_to_idx = {
            executor.submit(
                worker,
                i,
                all_dates[i]): i for i in range(all_dates_count)}

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_idx):
            try:
                result = future.result()
                i = result["i"]
                diameter = result["diameter_ms"]
                diameter_vertices = result["diameter"]
                vertices = result["num_vertices"]
                edges = result["num_edges"]
                current_radius_ms = result["radius_ms"]
                current_radius = result["radius"]
                k_core = result["k_core"]
                current_distances = result["distances"]
                max_k_core = result["max_k_core"]
                max_k_core_size = result["max_k_core_size"]
                avg_endpoint_distance = result["average_endpoint_distance"]
                avg_endpoint_distance_ms = result["average_endpoint_distance_ms"]

                if diameter is not None:
                    network_diameters_in_ms[i] = diameter
                    network_diameters_in_vertices[i] = diameter_vertices
                    num_vertices[i] = vertices
                    num_edges[i] = edges
                    radii_ms[i] = current_radius_ms
                    radii[i] = current_radius
                    k_core_sizes[i] = k_core
                    distances[i] = current_distances
                    max_k_cores[i] = max_k_core
                    max_k_core_sizes[i] = max_k_core_size
                    avg_endpoint_distances[i] = avg_endpoint_distance
                    avg_endpoint_distances_ms[i] = avg_endpoint_distance_ms

            except Exception as e:
                print(f"Error processing date: {e}")

    date_strings = [get_date_string(date) for date in all_dates]
    data = {
        "date": date_strings,
        "diameter_ms": network_diameters_in_ms,
        "diameter": network_diameters_in_vertices,
        "num_edges": num_edges,
        "num_vertices": num_vertices,
        "radius_ms": radii_ms,
        "radius": radii,
        "max_k_core": max_k_cores,
        "max_k_core_size": max_k_core_sizes,
        "average_endpoint_distance": avg_endpoint_distances,
        "average_endpoint_distance_ms": avg_endpoint_distances_ms,
        "time_interval": str(time_interval),
    }

    # Add distance columns properly
    for k in range(max_distance_data):
        data[f"{k}-distance"] = [distances[i][k]
                                 for i in range(all_dates_count)]
    # Add k-core columns properly
    for k in range(1, max_k_core_data):
        data[f"{k}-core"] = [k_core_sizes[i][k]
                             for i in range(all_dates_count)]

    return pd.DataFrame(data)


def main(args=None):
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output")
    parser.add_argument(
        "-o",
        "--output",
        help="Choose where to output. The output is a csv file.")
    parser.add_argument(
        "-r",
        "--range",
        help="Choose the range of dates to analyze",
        nargs=2)
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=1,
        help="Number of threads to use. Default is 1. Higher values may result in very high memory usage.")
    parser.add_argument(
        "-w",
        "--weighted_edges",
        action="store_true",
        help="Use graphs with weighted edges.")
    parser.add_argument(
        "-i",
        "--interval",
        help="What intervals to split the data into. Possible values: WEEK, MONTH, YEAR, ALL, default: WEEK",
        default="WEEK")
    # Parameters to measure
    parser.add_argument(
        "-d",
        "--diameter",
        action="store_true",
        help="Compute the diameter for the data. Can be computationally (and space) expensive.")
    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)
    print(args.range)
    time_interval = TimeInterval[args.interval.upper()]
    result = time_series_analysis(
        args.verbose,
        args.range,
        args.threads,
        args.weighted_edges,
        time_interval,
        diameter=args.diameter)
    result.to_csv(args.output, index=False)
    if args.verbose:
        print(f"Data saved to {args.output}")


if __name__ == '__main__':
    main()
