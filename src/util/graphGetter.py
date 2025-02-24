import graph_tool.all as gt
import os
import datetime
from .weekUtil import getWeek

def getGraphByDate(date: datetime.date) -> gt.Graph:
    inputFile : str = os.path.expanduser(f'''~/.cache/IPAnalysisTool/graphs/week/{datetime.datetime.strftime(getWeek(date)[0], "%Y-%m-%d")}.gt''')
    return gt.load_graph(inputFile)