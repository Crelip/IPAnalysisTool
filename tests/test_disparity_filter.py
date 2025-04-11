import sys

import pytest
import numpy as np
from graph_tool import Graph
from ip_analysis_tool.disparity_filter import disparity_filter, disparity_compute

# Helper function to compare two graphs
def graphs_equal(g1, g2):
    # Check basic counts
    if g1.num_vertices() != g2.num_vertices():
        print("Number of vertices does not match", file=sys.stderr)
        print(g1.num_vertices(), g2.num_vertices())
        return False
    if g1.num_edges() != g2.num_edges():
        print("Number of edges does not match", file=sys.stderr)
        return False

    # Check vertex IDs
    ids1 = set([g1.vp.ids[v] for v in g1.vertices()])
    ids2 = set([g2.vp.ids[v] for v in g2.vertices()])
    if not ids1 == ids2:
        print("Vertex IDs do not match", file=sys.stderr)
        print(ids1, ids2)
        return False

    # Check edges
    edges1 = {(g1.vp.ids[e.source()], g1.vp.ids[e.target()]) for e in g1.edges()}
    edges2 = {(g2.vp.ids[e.source()], g2.vp.ids[e.target()]) for e in g2.edges()}

    return edges1 == edges2

@pytest.fixture
def dummy_input_graph_1():
    g = Graph(
        [
            ("1", "2", 2999),
            ("1", "31", 3500),
            ("2", "3", 2907),
            ("2", "21", 150),
            ("2", "31", 2465),
            ("3", "21", 105),
            ("3", "4", 226),
            ("3", "5", 455),
            ("3", "8", 1565),
            ("3", "16", 177),
            ("4", "22", 222),
            ("5", "6", 282),
            ("5", "14", 174),
            ("6", "7", 309),
            ("7", "10", 305),
            ("8", "9", 1565),
            ("9", "11", 586),
            ("9", "15", 781),
            ("10", "23", 127),
            ("10", "24", 104),
            ("11", "12", 294),
            ("11", "13", 293),
            ("12", "25", 108),
            ("13", "26", 125),
            ("14", "27", 153),
            ("15", "17", 723),
            ("16", "28", 143),
            ("17", "18", 720),
            ("18", "19", 347),
            ("18", "20", 374),
            ("19", "29", 101),
            ("20", "30", 117)
        ],
        eprops=[("traversals", "int")],
        hashed=True,
        directed=True
    )
    g.gp["metadata"] = g.new_graph_property("string")
    g.gp.metadata = '{"date": "2021-01-01"}'
    return g

@pytest.fixture
def dummy_output_values_1():
    return [
        1.0000000050247593e-08,
        0.0,
        1.1102230246251565e-16,
        0.0,
        0.0,
        0.0,
        0.0,
        9.999999999998899e-05,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        9.999999999998899e-05,
        0.0,
        0.0,
        0.0,
        9.999999999998899e-05,
        0.0,
        0.0,
        9.999999999998899e-05,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        9.999999999998899e-05,
        0.0,
        0.0,
        0.0,
        0.0
    ]

@pytest.fixture
def dummy_output_graph_1():
    g = Graph(
        [
            ("3", "5", 455),
            ("8", "9", 1565),
            ("7", "10", 305),
            ("9", "11", 586),
            ("17", "18", 720),
        ],
        eprops=[("traversals","int")],
        hashed=True,
        directed=True
    )
    g.gp["metadata"] = g.new_graph_property("string")
    g.gp.metadata = '{"date": "2021-01-01"}'
    return g

# Filtered graph with no edges should be an empty graph
@pytest.fixture
def dummy_input_graph_empty():
    g = Graph(
        directed=False,
    )
    g.ep["traversals"] = g.new_edge_property("int")
    for _ in range(20): g.add_vertex()
    g.gp["metadata"] = g.new_graph_property("string")
    g.gp.metadata = '{"date": "2023-09-30"}'
    return g

def test_disparity_filter_1(dummy_input_graph_1, dummy_output_values_1, dummy_output_graph_1):
    computed_graph, computed_values = disparity_compute(dummy_input_graph_1)
    for i, e in enumerate(computed_graph.edges()):
        assert computed_graph.ep.alpha[e] == dummy_output_values_1[i]
    computed_graph = disparity_filter(dummy_input_graph_1)
    assert graphs_equal(computed_graph, dummy_output_graph_1)

def test_disparity_filter_empty(dummy_input_graph_empty):
    computed_graph = disparity_filter(dummy_input_graph_empty)
    assert computed_graph.num_vertices() == 0
    assert computed_graph.num_edges() == 0