import graph_tool.all as gt
from graph_tool.topology import similarity

from hBackbone import hBackbone
from kcore import kcoreDecomposition
from datetime import date

def edgeRepr(e, ipProp):
    src = ipProp[e.source()]
    tgt = ipProp[e.target()]
    return tuple(sorted([src, tgt]))

def compareKCoreAndHBackbone(datetime: date):
    hBackboneGraph = hBackbone(datetime, output="graph")
    kCoreData = kcoreDecomposition(datetime, output="graph")
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

if __name__ == "__main__":
    from argparse import ArgumentParser
    from json import dumps
    import datetime

    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    args = parser.parse_args()
    # hBackbone(datetime.datetime.strptime(args.date, "%Y-%m-%d").date(), modifier=args.modifier, visualize=args.visualize)
    print(dumps(compareKCoreAndHBackbone(datetime.datetime.strptime(args.date, "%Y-%m-%d").date()), indent=2))