import graph_tool.all as gt
import os
import datetime
from .weekUtil import getWeek

def getGraphByDate(date: datetime.date, weightedEdges = False) -> gt.Graph:
    inputFile : str = os.path.expanduser(f'''~/.cache/IPAnalysisTool/graphs/week/{'base' if not weightedEdges else 'weighted'}/{datetime.datetime.strftime(getWeek(date)[0], "%Y-%m-%d")}.gt''')
    return gt.load_graph(inputFile)

def getAllGraphDates(weightedEdges = False):
    return [datetime.datetime.strptime(f[:-3], "%Y-%m-%d").date() for f in sorted(os.listdir(os.path.expanduser(f"~/.cache/IPAnalysisTool/graphs/week/{'base' if not weightedEdges else 'weighted'}")))]