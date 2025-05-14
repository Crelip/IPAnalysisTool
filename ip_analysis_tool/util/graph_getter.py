from graph_tool import Graph, load_graph
import os
import datetime
from .date_util import get_parent_week, get_parent_interval
from ..enums import TimeInterval

def get_graph_by_date(date: datetime.date = None, weighted_edges = False, time_interval : TimeInterval = TimeInterval.WEEK) -> Graph:
    """
    Returns the graph for the week containing the given date.
    :param date: The date to get the graph for (can be either datetime.date, or string in format YYYY-MM-DD). (datetime.date or str)
    :param weighted_edges: Whether to get the graph with weighted edges. Default is False. Graphs with weighted edges have much less data. (bool)
    :param time_interval: Specify the time interval, for which the measurement data should be returned (ip_analysis_tool.enums.TimeInterval)
    :return: The graph for the specified interval and weight. (graph_tool.Graph)
    """
    from graph_tool import load_graph
    if time_interval == TimeInterval.ALL:
        return load_graph(os.path.expanduser(f"""~/.cache/IPAnalysisTool/graphs/all/{'weighted' if weighted_edges else 'base'}/all.gt"""))
    if type(date) != datetime.date:
        try:
            from .date_util import get_date_object
            date = get_date_object(date)
        except:
            print("Invalid date format.")
    input_file : str = os.path.expanduser(f'''~/.cache/IPAnalysisTool/graphs/{str(time_interval).lower()}/{'base' if not weighted_edges else 'weighted'}/{datetime.datetime.strftime(get_parent_interval(date, time_interval=time_interval)[0], "%Y-%m-%d")}.gt''')
    return load_graph(input_file)

def get_all_graph_dates(weighted_edges = False, time_interval : TimeInterval = TimeInterval.WEEK) -> list:
    """
    Returns a list of all dates for which graphs are available.
    :param weighted_edges: Whether to get the range for graphs with weighted edges. Default is False. Graphs with weighted edges have much less data. (bool)
    :return: A list of all dates for which graphs with the specified edge weighting are available. (list)
    """
    return [datetime.datetime.strptime(f[:-3], "%Y-%m-%d").date() for f in sorted(os.listdir(os.path.expanduser(f"~/.cache/IPAnalysisTool/graphs/{str(time_interval).lower()}/{'base' if not weighted_edges else 'weighted'}")))]