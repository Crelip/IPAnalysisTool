from math import floor

import graph_tool.all as gt
import os
import datetime
from json import dumps
from util.graphGetter import getGraphByDate
from util.calculations import getHIndex
from util.graphManipulation import addInverseEP

# Get bridge of the network
def getBridge(g: gt.Graph):
    inverse = g.new_edge_property("float")
    g.edge_properties["minEdgeInverse"] = inverse
    for e in g.edges():
        inverse[e] = 1 / g.ep.minEdge[e]
    vertexBetweenness, edgeBetweenness = gt.betweenness(g, weight=g.ep.minEdgeInverse)
    edgeBetweenness = {e: edgeBetweenness[e] * 100000000 for e in g.edges()}
    print(g.num_vertices())
    print(max([edgeBetweenness[e] for e in g.edges()]))

    vertexAmount = g.num_vertices()
    # Bridge measurement
    return {e: edgeBetweenness[e] / vertexAmount for e in g.edges()}

# Get H-Bridge of the network
def getHBridge(g: gt.Graph, bridge = None) -> int:
    if bridge == None: bridge = getBridge(g)
    # H-Bridge calculation using h-index algorithm
    return getHIndex(g, bridge, count=g.num_edges())

def getHStrength(g: gt.Graph, inv) -> int:
    # H-strength calculation using h-index algorithm
    return getHIndex(g.vertices(), inv)

def hBackbone(date: datetime.date):
    g : gt.Graph = getGraphByDate(date)
    inv = addInverseEP(g)
    bridge = getBridge(g)
    # H-Bridge calculation
    HBridge : int = getHBridge(g, bridge)
    print(f"HBridge: {HBridge}")
    print(f"HStrength: {getHStrength(g, inv)}")

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    args = parser.parse_args()
    hBackbone(datetime.datetime.strptime(args.date, "%Y-%m-%d").date())
    