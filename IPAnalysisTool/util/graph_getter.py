from graph_tool import Graph
import os
import datetime
from .weekUtil import getWeek

def get_graph_by_date(date, weightedEdges = False) -> Graph:
    """
    Returns the graph for the week containing the given date.
    :param date: The date to get the graph for (can be either datetime.date, or string in format YYYY-MM-DD). (datetime.date or str)
    :param weightedEdges: Whether to get the graph with weighted edges. Default is False. Graphs with weighted edges have much less data. (bool)
    :return: The graph for the specified week and weight. (graph_tool.Graph)
    """
    if type(date) != datetime.date:
        try:
            from .weekUtil import getDateObject
            date = getDateObject(date)
        except:
            print("Invalid date format.")
    from graph_tool import load_graph
    inputFile : str = os.path.expanduser(f'''~/.cache/IPAnalysisTool/graphs/week/{'base' if not weightedEdges else 'weighted'}/{datetime.datetime.strftime(getWeek(date)[0], "%Y-%m-%d")}.gt''')
    return load_graph(inputFile)

def get_all_graph_dates(weightedEdges = False):
    """
    Returns a list of all dates for which graphs are available.
    :param weightedEdges: Whether to get the range for graphs with weighted edges. Default is False. Graphs with weighted edges have much less data. (bool)
    :return: A list of all dates for which graphs with the specified edge weighting are available. (list)
    """
    return [datetime.datetime.strptime(f[:-3], "%Y-%m-%d").date() for f in sorted(os.listdir(os.path.expanduser(f"~/.cache/IPAnalysisTool/graphs/week/{'base' if not weightedEdges else 'weighted'}")))]