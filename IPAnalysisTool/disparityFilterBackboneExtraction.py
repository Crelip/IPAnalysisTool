# Based on https://github.com/DerwenAI/disparity_filter
from graph_tool import Graph, GraphView
from scipy.stats import percentileofscore
from .util.graphManipulation import removeReciprocalEdges

def disparityIntegral(x, k):
    assert x != 1.0, "x cannot be 1.0"
    assert k != 1.0, "k cannot be 1.0"
    return ((1.0 - x) ** k) / ((k - 1.0) * (x - 1.0))

def getDisparitySignificance(normWeight, degree):
    return 1.0 - ((degree - 1.0) * (disparityIntegral(normWeight, degree) - disparityIntegral(0.0, degree)))

def disparityCompute(g : Graph):
    alphaMeasures = []
    gv = Graph(g, directed = False)
    # Scale back the weights for edges
    maxWeight = max([g.ep.traversals[e] for e in gv.edges()])
    weightProp = gv.new_edge_property("float")
    for e in gv.edges():
        weightProp[e] = gv.ep.traversals[e] / maxWeight
    strengthProp = gv.new_vertex_property("float")
    edgeNormWeight = gv.new_edge_property("float")
    edgeAlpha = gv.new_edge_property("float")
    edgeAlphaPercentile = gv.new_edge_property("float")
    for v in gv.vertices():
        degree = v.out_degree()
        strength = 0.0
        for e in v.in_edges():
            strength += weightProp[e]
        strengthProp[v] = strength
        for e in v.in_edges():
            normWeight = weightProp[e] / strength
            edgeNormWeight[e] = normWeight

            if degree > 1:
                try:
                    if normWeight == 1.0:
                        normWeight -= 0.0001

                    alpha = getDisparitySignificance(normWeight, degree)
                except AssertionError:
                    print("AssertionError")
                    quit(1)
                edgeAlpha[e] = alpha
                alphaMeasures.append(alpha)
            else:
                edgeAlpha[e] = 0.0

    for e in gv.edges():
        edgeAlphaPercentile[e] = percentileofscore(alphaMeasures, edgeAlpha[e])

    gv.edge_properties["alpha"] = edgeAlpha
    gv.edge_properties["alphaPercentile"] = edgeAlphaPercentile
    return gv, alphaMeasures

def disparityFilter(g : Graph, percentileThreshold = 50.0):
    gv, alphaMeasures = disparityCompute(g)
    edgeAlphaPercentile = gv.ep.alphaPercentile

    # Create edge and vertex filter properties
    edge_filter = gv.new_edge_property("bool")
    for e in gv.edges():
        edge_filter[e] = edgeAlphaPercentile[e] >= percentileThreshold

    # Apply the edge filter
    gv = GraphView(g, directed = False, efilt=edge_filter)
    print(gv.num_edges())

    # Get rid of duplicite edges
    gv = removeReciprocalEdges(gv)

    # Remove vertices with degree less than 2 - iterate until no vertices are removed
    prune = True
    while prune:
        prune = False
        degrees = gv.degree_property_map("total")
        vfilt = gv.new_vertex_property("bool")
        for v in gv.vertices():
            vfilt[v] = degrees[v] >= 2
            # One vertex with degree < 2 is enough to trigger another iteration
            if not vfilt[v]: prune = True
        gv = GraphView(gv, vfilt=vfilt)

    return gv

def main():
    from argparse import ArgumentParser
    from IPAnalysisTool.util.graphGetter import getGraphByDate
    from IPAnalysisTool.visualize import baseVisualize
    from IPAnalysisTool.util.weekUtil import getDateObject
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Date to process", type=str)
    parser.add_argument("-p", "--percentile", help="Percentile threshold", type=float, default=50.0)
    parser.add_argument("-w", "--weighted", help="Weighted edges", action="store_true")
    args = parser.parse_args()
    g = disparityFilter(getGraphByDate(getDateObject(args.date)), args.percentile)
    print(g.num_vertices())
    baseVisualize(g, f"disparity_{args.date}")

if __name__ == "__main__":
    main()