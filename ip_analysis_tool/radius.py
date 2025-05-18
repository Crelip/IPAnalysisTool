from graph_tool import Graph


def radius(g: Graph, input_property: str = "avg") -> float:
    """
    Calculate the radius of a graph based on the given property.
    :param g: Graph to calculate the radius for
    :param input_property: The property to calculate the radius for
    :return: Radius of the graph - typically the highest value of the given property in the graph
    """
    if input_property == "avg":
        prop = g.vp.avg_distance
    elif input_property == "min":
        prop = g.vp.min_distance
    elif input_property == "max":
        prop = g.vp.max_distance
    return max(prop[v] for v in g.vertices)