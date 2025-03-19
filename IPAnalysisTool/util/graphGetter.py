from graph_tool import Graph
import os
import datetime
from .weekUtil import getWeek

def getGraphByDate(date: datetime.date, weightedEdges = False) -> Graph:
    from graph_tool import load_graph
    inputFile : str = os.path.expanduser(f'''~/.cache/IPAnalysisTool/graphs/week/{'base' if not weightedEdges else 'weighted'}/{datetime.datetime.strftime(getWeek(date)[0], "%Y-%m-%d")}.gt''')
    return load_graph(inputFile)

def getAllGraphDates(weightedEdges = False):
    return [datetime.datetime.strptime(f[:-3], "%Y-%m-%d").date() for f in sorted(os.listdir(os.path.expanduser(f"~/.cache/IPAnalysisTool/graphs/week/{'base' if not weightedEdges else 'weighted'}")))]