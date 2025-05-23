from typing import Tuple
from graph_tool import Graph, GraphView
from scipy.stats import percentileofscore


def disparity_integral(x, k):
    assert x != 1.0, "x cannot be 1.0"
    assert k != 1.0, "k cannot be 1.0"
    return ((1.0 - x) ** k) / ((k - 1.0) * (x - 1.0))


def get_disparity_significance(norm_weight, degree):
    return 1.0 - ((degree - 1.0) * (disparity_integral(norm_weight,
                  degree) - disparity_integral(0.0, degree)))


def disparity_compute(g: Graph) -> Tuple[Graph, dict]:
    """
    Compute the disparity measures of a graph.
    :param g: Input graph.
    :return: A tuple of the graph and the disparity measures.
    """
    if g.num_edges() == 0:
        return Graph(), {}
    alpha_measures = []
    gv = Graph(g, directed=False)
    # Scale back the weights for edges
    max_weight = max([g.ep.traversals[e] for e in gv.edges()])
    weight_prop = gv.new_edge_property("float")
    for e in gv.edges():
        weight_prop[e] = gv.ep.traversals[e] / max_weight
    strength_prop = gv.new_vertex_property("float")
    edge_norm_weight = gv.new_edge_property("float")
    edge_alpha = gv.new_edge_property("float")
    edge_alpha_percentile = gv.new_edge_property("float")
    for v in gv.vertices():
        degree = v.out_degree()
        strength = 0.0
        for e in v.in_edges():
            strength += weight_prop[e]
        strength_prop[v] = strength
        for e in v.in_edges():
            normWeight = weight_prop[e] / strength
            edge_norm_weight[e] = normWeight

            if degree > 1:
                try:
                    if normWeight == 1.0:
                        normWeight -= 0.0001

                    alpha = get_disparity_significance(normWeight, degree)
                except AssertionError:
                    print("AssertionError")
                    quit(1)
                edge_alpha[e] = alpha
                alpha_measures.append(alpha)
            else:
                edge_alpha[e] = 0.0

    for e in gv.edges():
        edge_alpha_percentile[e] = percentileofscore(
            alpha_measures, edge_alpha[e])

    gv.edge_properties["alpha"] = edge_alpha
    gv.edge_properties["alpha_percentile"] = edge_alpha_percentile
    return gv, alpha_measures


def disparity_filter(g: Graph, percentile_threshold: float = 50.0) -> Graph:
    """
    Filter a graph based on the disparity filter.
    :param g: Input graph.
    :param percentile_threshold: The threshold for the percentile of edges. Default is 50.
    :return: Filtered graph.
    """
    if g.num_edges() == 0:
        return Graph()
    gv, alpha_measures = disparity_compute(g)
    edge_alpha_percentile = gv.ep.alpha_percentile

    # Create edge and vertex filter properties
    efilt = gv.new_edge_property("bool")
    for e in gv.edges():
        efilt[e] = edge_alpha_percentile[e] >= percentile_threshold

    # Apply the edge filter
    gv = GraphView(g, directed=False, efilt=efilt)

    vfilt = gv.new_vertex_property("bool")
    for v in gv.vertices():
        vfilt[v] = v.out_degree() + v.in_degree() > 0

    gv = GraphView(gv, directed=False, vfilt=vfilt)
    return gv


def main():
    from argparse import ArgumentParser
    from ip_analysis_tool.util.graph_getter import get_graph_by_date
    from ip_analysis_tool.visualize.graph import visualize_graph
    from ip_analysis_tool.util.date_util import get_date_object
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Date to process", type=str)
    parser.add_argument(
        "-p",
        "--percentile",
        help="Percentile threshold",
        type=float,
        default=50.0)
    parser.add_argument(
        "-w",
        "--weighted_edges",
        help="Use graphs with weighted edges.",
        action="store_true")
    args = parser.parse_args()
    g = disparity_filter(
        get_graph_by_date(
            get_date_object(
                args.date),
            weighted_edges=args.weighted_edges),
        args.percentile)
    print(g.num_vertices())
    visualize_graph(g, f"disparity_{args.date}")


if __name__ == "__main__":
    main()
