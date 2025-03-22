import graph_tool.all as gt
from datetime import date

def edge_repr(e, ip_prop):
    src = ip_prop[e.source()]
    tgt = ip_prop[e.target()]
    return tuple(sorted([src, tgt]))

def compare_graphs_jaccard(g1: gt.Graph, g2: gt.Graph):
    # Apply Jaccard index for edges
    edges1 = {edge_repr(e, g1.vp.ip) for e in g1.edges()}
    edges2 = {edge_repr(e, g2.vp.ip) for e in g2.edges()}
    edges_in_intersection = edges1.intersection(edges2)
    edges_in_union = edges1.union(edges2)
    similarity = len(edges_in_intersection) / len(edges_in_union)
    return {
        "vertices_in_graph_1": g1.num_vertices(),
        "edges_in_graph_1": g1.num_edges(),
        "vertices_in_graph_2": g2.num_vertices(),
        "edges_in_graph_2": g2.num_edges(),
        "intersection_of_edges": len(edges_in_intersection),
        "union_of_edges": len(edges_in_union),
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
    # print(dumps(compare_k_core_and_h_backbone(datetime.datetime.strptime(args.date, "%Y-%m-%d").date()), indent=2))