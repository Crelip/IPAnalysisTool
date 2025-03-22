from graph_tool import Graph

def radius(g : Graph, input_property: str = "avg") -> float:
    """
    Calculate the radius of a graph based on the given property.
    :param g: Graph to calculate the radius for
    :param input_property: The property to calculate the radius for
    :return: Radius of the graph - typically the highest value of the given property in the graph
    """
    if input_property == "avg": prop = g.vp.avg_distance
    elif input_property == "min": prop = g.vp.min_distance
    elif input_property == "max": prop = g.vp.max_distance
    return max(prop[v] for v in g.vertices)

# Return the radius of a graph in the form of a string on stdout
def main():
    from argparse import ArgumentParser
    from .util.graph_getter import get_graph_by_date
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates a graph for the week containing the given date.")
    parser.add_argument("-p", "--property", default="avg", help="The property to calculate the radius for.")
    args = parser.parse_args()
    if args.date:
        print(radius(get_graph_by_date(args.date), input_property=args.property))
    else:
        print("Please provide a date.")
        exit(1)

if __name__ == "__main__":
    main()