import graph_tool.all as gt
from datetime import date

def edgeRepr(e, ipProp):
    src = ipProp[e.source()]
    tgt = ipProp[e.target()]
    return tuple(sorted([src, tgt]))

# About to deprecate this function, redundant code
def compareKCoreAndHBackbone(datetime: date):
    from hBackbone import hBackbone
    from kcore import kCoreDecompositionFromDate
    hBackboneGraph = hBackbone(datetime, output="graph")
    kCoreData = kCoreDecompositionFromDate(datetime, output="graph")
    print(kCoreData)
    kCoreGraph, kCore = kCoreData[0], kCoreData[1]
    maxK = max(kCore[v] for v in kCoreGraph.vertices())
    verticesAmountInHBackbone = hBackboneGraph.num_vertices()
    edgesAmountInHBackbone = hBackboneGraph.num_edges()
    hBackboneEdges = {edgeRepr(e, hBackboneGraph.vp.ip) for e in hBackboneGraph.edges()}
    vertex_filter = kCoreGraph.new_vertex_property("bool")
    result = {}
    # Apply Jaccard index for edges
    for i in range(1, maxK + 1):
        for v in kCoreGraph.vertices(): vertex_filter[v] = (kCore[v] >= i)
        kCoreGraph.set_vertex_filter(vertex_filter)
        verticesAmountInKCore = kCoreGraph.num_vertices()
        edgesAmountInKCore = kCoreGraph.num_edges()
        kCoreEdges = {edgeRepr(e, kCoreGraph.vp.ip) for e in kCoreGraph.edges()}
        edgesInIntersection = kCoreEdges.intersection(hBackboneEdges)
        edgesInUnion = kCoreEdges.union(hBackboneEdges)
        similarity = len(edgesInIntersection) / len(edgesInUnion)
        result[i] = {
            "verticesInKCore": verticesAmountInKCore,
            "edgesInKCore": edgesAmountInKCore,
            "verticesInHBackbone": verticesAmountInHBackbone,
            "edgesInHBackbone": edgesAmountInHBackbone,
            "intersection": len(edgesInIntersection),
            "union": len(edgesInUnion),
            "similarity": similarity
        }
    return result

def compareGraphsJaccard(g1: gt.Graph, g2: gt.Graph):
    # Apply Jaccard index for edges
    edges1 = {edgeRepr(e, g1.vp.ip) for e in g1.edges()}
    edges2 = {edgeRepr(e, g2.vp.ip) for e in g2.edges()}
    edgesInIntersection = edges1.intersection(edges2)
    edgesInUnion = edges1.union(edges2)
    similarity = len(edgesInIntersection) / len(edgesInUnion)
    return {
        "verticesInG1": g1.num_vertices(),
        "edgesInG1": g1.num_edges(),
        "verticesInG2": g2.num_vertices(),
        "edgesInG2": g2.num_edges(),
        "intersection": len(edgesInIntersection),
        "union": len(edgesInUnion),
        "similarity": similarity
    }

if __name__ == "__main__":
    from argparse import ArgumentParser
    from json import dumps
    import datetime

    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    args = parser.parse_args()
    # hBackbone(datetime.datetime.strptime(args.date, "%Y-%m-%d").date(), modifier=args.modifier, visualize=args.visualize)
    print(dumps(compareKCoreAndHBackbone(datetime.datetime.strptime(args.date, "%Y-%m-%d").date()), indent=2))