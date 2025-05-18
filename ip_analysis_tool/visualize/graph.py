from graph_tool import Graph, GraphView, VertexPropertyMap

def visualize_graph(
        g: Graph,
        name: str,
        prop: str = "ip",
        output_size: tuple = (10000, 10000),
):
    """
    Visualizes the graph on a plain background. The result is output to a file.
    :param g: Input graph.
    :param name: Filename of the output picture.
    :param prop: What property to show within nodes. Defaults to "ip".
    :param output_size: Resolution of the output picture as a tuple (width, height).
    :return:
    """
    from graph_tool.all import graph_draw, sfdp_layout
    graph_draw(
            g,
            sfdp_layout(g),
            output_size=output_size,
            vertex_text=g.vertex_index if prop== "vertex_index" else g.vp[prop],
            vertex_font_size=8,
            vertex_size=6,
            edge_pen_width=2.0,
            bg_color=[1,1,1,1],
            vertex_fill_color=(1, 0, 0, .5),
            output=f"{name}"
                  )

def visualize_graph_map(
        g: Graph,
        name: str = None,
        geo_data: dict = None,
        show: bool = True,
        save: bool = True,
        directed: bool = False,
):
    """
    Visualizes the graph on a map background. The result is output to a file.
    :param g: Input graph.
    :param name: Filename of the output picture.
    :param geo_data: An optional dict containing geographic data for IP addresses. If none, it uses ip_analysis_tool.util.geo_data_util's get_geo_data() to gather the relevant data.
    :param show: Whether to directly show the resulting picture. Defaults to True.
    :param save: Whether to save the resulting picture. Defaults to True.
    :param directed: Whether to show arrows on the resulting picture. Defaults to False.
    :return:
    """
    g = GraphView(g, directed=directed)
    from graph_tool.all import graph_draw, group_vector_property
    from mpl_toolkits.basemap import Basemap
    import matplotlib.pyplot as plt
    if geo_data is None:
        from ip_analysis_tool.util.geo_data_util import get_geo_data
        geo_data = get_geo_data(g.vp.ip[v] for v in g.vertices())

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    lon = g.new_vertex_property("float")
    lat = g.new_vertex_property("float")
    vfilt = g.new_vertex_property("bool")
    # Collect the coordinates of the vertices, if there's none, filter them out
    for v in g.vertices():
        ip = g.vp.ip[v]
        if ip in geo_data and geo_data[ip] is not None:
            lon[v] = geo_data[ip]["location"]["longitude"]
            lat[v] = geo_data[ip]["location"]["latitude"]
            vfilt[v] = True
        else:
            vfilt[v] = False
    g.set_vertex_filter(vfilt)

    pos = group_vector_property([lon, lat])
    m = Basemap(
        projection="merc",
        resolution="i",
        llcrnrlat=-60,
        urcrnrlat=80,
        llcrnrlon=-180,
        urcrnrlon=180,
    )

    m.shadedrelief(scale=.2)

    a = graph_draw(g,
                pos=pos.t(lambda x: m(*x)),
                edge_color=(.1, .1, .1, .1),
                mplfig=ax,
                vertex_fill_color=(1, 0, 0, .5),
                   )

    #a.fit_view()
    a.set_zorder(10)
    plt.tight_layout()
    if save:
        fig.savefig(f"{name}", dpi=1200, bbox_inches='tight')
        print("Saved picture to", f"{name}")
    if show: plt.show()

def main(args = None):
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Date of network graph to visualize.", required=True)
    parser.add_argument(
        "-i",
        "--interval",
        help="What interval to visualize the graph for. Possible values: WEEK, MONTH, YEAR, ALL, default: WEEK",
        default="WEEK")
    parser.add_argument("-n", "--name", help="Filename of the output picture.")
    parser.add_argument("-m", "--map", help="Visualize on a map background.", action="store_true")
    parser.add_argument("-s", "--show", help="Show graph directly, applies to map visualization only.", action="store_true")
    args = parser.parse_args(args)
    from ip_analysis_tool.util.graph_getter import get_graph_by_date
    from ip_analysis_tool.util.date_util import get_date_object
    from ip_analysis_tool.enums import TimeInterval
    g = get_graph_by_date(
        get_date_object(args.date),
        time_interval=TimeInterval[args.interval.upper()]
    )
    if args.map:
        visualize_graph_map(g, name=args.name, show=args.show, save=True)
    else:
        visualize_graph(g, args.name)

if __name__ == "__main__":
    main()
