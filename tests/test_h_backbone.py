import sys

import pytest
import numpy as np
from graph_tool import Graph
from ip_analysis_tool.h_backbone import h_backbone

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
    ids1 = np.array([g1.vp.ids[v] for v in g1.vertices()])
    ids2 = np.array([g2.vp.ids[v] for v in g2.vertices()])
    if not np.array_equal(ids1, ids2):
        print("Vertex IDs do not match", file=sys.stderr)
        print(ids1, ids2)
        return False

    # Check edges
    edges1 = {(g1.vp.ids[e.source()], g1.vp.ids[e.target()]) for e in g1.edges()}
    edges2 = {(g2.vp.ids[e.source()], g2.vp.ids[e.target()]) for e in g2.edges()}

    return edges1 == edges2

# Simple graph
@pytest.fixture
def dummy_input_graph_1():
    g = Graph(
        [
            ("1", "3", 2),
            ("2", "3", 1),
            ("3", "5", 8), #Should stay in h-backbone
            ("3", "6", 5), #Should stay in h-backbone
            ("4", "5", 1),
            ("5", "6", 4), #Should stay in h-backbone
            ("6", "7", 6), #Should stay in h-backbone
            ("7", "8", 3),
            ("7", "9", 1),
            ("7", "10", 2)
        ],
        eprops=[("traversals", "int")],
        hashed=True,
        directed=False)
    g.gp["metadata"] = g.new_graph_property("string")
    g.gp.metadata = '{"date": "2021-01-01"}'
    return g

@pytest.fixture
def dummy_output_graph_1():
    g = Graph(
        [
            ("3", "5", 8),
            ("3", "6", 5),
            ("5", "6", 4),
            ("6", "7", 6),
        ],
        eprops=[("traversals", "int")],
        hashed=True,
        directed=False)
    g.gp["metadata"] = g.new_graph_property("string")
    g.gp.metadata = '{"date": "2021-01-01"}'
    return g

@pytest.fixture
def dummy_input_graph_2():
    g = Graph(
        [
            ("1", "4", 1),
            ("2", "4", 1),
            ("3", "4", 1),
            ("4", "5", 6), #Should stay in h-backbone
            ("5", "6", 2),
            ("5", "9", 1),
            ("5", "11", 1), #Should stay in h-backbone
            ("5", "15", 4), #Should stay in h-backbone
            ("5", "16", 5), #Should stay in h-backbone
            ("5", "18", 1), #Should stay in h-backbone
            ("6", "7", 1),
            ("6", "8", 1),
            ("10", "11", 3),
            ("11", "12", 1),
            ("11", "13", 1),
            ("11", "14", 3),
            ("16", "17", 1),
            ("18", "19", 5), #Should stay in h-backbone
            ("18", "20", 1),
            ("18", "21", 1),
            ("18", "22", 4), #Should stay in h-backbone
        ],
        eprops=[("traversals", "int")],
        hashed=True,
        directed=False
    )
    g.gp["metadata"] = g.new_graph_property("string")
    g.gp.metadata = '{"date": "2022-05-12"}'
    return g

@pytest.fixture
def dummy_output_graph_2():
    g = Graph(
        [
            ("4", "5", 6),
            ("5", "11", 1),
            ("5", "15", 4),
            ("5", "16", 5),
            ("5", "18", 1),
            ("18", "19", 5),
            ("18", "22", 4),
        ],
        eprops=[("traversals", "int")],
        hashed=True,
        directed=False
    )
    g.gp["metadata"] = g.new_graph_property("string")
    g.gp.metadata = '{"date": "2022-05-12"}'
    return g

@pytest.fixture
def dummy_input_graph_3():
    g = Graph(
        [
            ("1", "2", 3),
            ("1", "3", 4), # Should stay in h-backbone
            ("1", "4", 6), # Should stay in h-backbone
            ("1", "5", 1), # Should stay in h-backbone
            ("5", "6", 2),
            ("5", "7", 3),
            ("5", "8", 9), # Should stay in h-backbone
            ("5", "9", 5), # Should stay in h-backbone
        ],
        eprops=[("traversals", "int")],
        hashed=True,
        directed=False
    )
    g.gp["metadata"] = g.new_graph_property("string")
    g.gp.metadata = '{"date": "2023-09-30"}'
    return g

@pytest.fixture
def dummy_output_graph_3():
    g = Graph(
        [
            ("1", "3", 4),
            ("1", "4", 6),
            ("1", "5", 1),
            ("5", "8", 9),
            ("5", "9", 5),
        ],
        eprops=[("traversals", "int")],
        hashed=True,
        directed=False
    )
    g.gp["metadata"] = g.new_graph_property("string")
    g.gp.metadata = '{"date": "2023-09-30"}'
    return g

# H-backbone of a graph with no edges should be an empty graph
@pytest.fixture
def dummy_input_graph_4():
    g = Graph(
        directed=False,
    )
    g.ep["traversals"] = g.new_edge_property("int")
    for _ in range(20): g.add_vertex()
    g.gp["metadata"] = g.new_graph_property("string")
    g.gp.metadata = '{"date": "2023-09-30"}'
    return g

def test_h_backbone_1(dummy_input_graph_1, dummy_output_graph_1):
    result = h_backbone(dummy_input_graph_1, visualize=False, output="graph", verbose=False)
    assert graphs_equal(result, dummy_output_graph_1)

def test_h_backbone_2(dummy_input_graph_2, dummy_output_graph_2):
    result = h_backbone(dummy_input_graph_2, visualize=False, output="graph", verbose=False)
    assert graphs_equal(result, dummy_output_graph_2)

def test_h_backbone_3(dummy_input_graph_3, dummy_output_graph_3):
    result = h_backbone(dummy_input_graph_3, visualize=False, output="graph", verbose=False)
    assert graphs_equal(result, dummy_output_graph_3)

# H-backbone of a graph with no edges should be an empty graph
def test_h_backbone_4(dummy_input_graph_4):
    result = h_backbone(dummy_input_graph_4, visualize=False, output="graph", verbose=False)
    assert result.num_vertices() == 0, "H-backbone of a graph with no edges should be an empty graph"
    assert result.num_edges() == 0, "H-backbone of a graph with no edges should be an empty graph"