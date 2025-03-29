from graph_tool import Graph, VertexPropertyMap

def get_color_hops(g: Graph) -> VertexPropertyMap:
    """
    Assigns a color to each vertex based on its hop distance from the root vertex.
    :param g: The graph to visualize.
    :return: VertexPropertyMap with colors for each vertex.
    """
    import matplotlib.cm as cm
    colormap = cm.viridis
    color_map = g.new_vertex_property("vector<double>")
    for v in g.vertices():
        norm_val = g.vp.hop_distance[v] / 40.0
        color_map[v] = colormap(norm_val)
    return color_map

def visualize_graph(
        g: Graph,
        name: str,
        prop: str = "ip",
        color_hops = False
):
    from graph_tool.all import graph_draw, sfdp_layout
    if color_hops:
        color_map = get_color_hops(g)
    graph_draw(
            g,
            sfdp_layout(g),
            output_size=(10000,10000),
            vertex_text=g.vertex_index if prop== "vertex_index" else g.vp[prop],
            vertex_font_size=8,
            vertex_size=6,
            edge_pen_width=2.0,
            bg_color=[1,1,1,1],
            vertex_fill_color=color_map if color_hops else (1, 0, 0, .5),
            output=f"scratchpad/{name}.svg"
                  )

def visualize_graph_map(
        g: Graph,
        name: str,
        geo_data = None,
        color_hops = False,
        show = True,
        save = True
):
    from graph_tool.all import graph_draw, group_vector_property
    from mpl_toolkits.basemap import Basemap
    import matplotlib.pyplot as plt
    if geo_data is None:
        from ip_analysis_tool.util.geo_data_util import get_geo_data
        geo_data = get_geo_data(g.vp.ip[v] for v in g.vertices())

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    lon = g.new_vertex_property("float")
    lat = g.new_vertex_property("float")
    for v in g.vertices():
        ip = g.vp.ip[v]
        try:
            if ip in geo_data and geo_data[ip] is not None:
                lon[v] = geo_data[ip]["location"]["longitude"]
                lat[v] = geo_data[ip]["location"]["latitude"]
        except Exception as e:
            print(f"Error positioning vertex for IP {ip}: {e}")

    if color_hops:
        color_map = get_color_hops(g)

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
                vertex_fill_color=color_map if color_hops else (1, 0, 0, .5),
                   )

    a.fit_view()
    a.set_zorder(10)
    plt.tight_layout()
    if show: plt.show()
    if save: fig.savefig(f"scratchpad/{name}.svg", dpi=1200, bbox_inches='tight')

def main(args = None):
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-n", "--name", help="Name of the graph")
    parser.add_argument("-p", "--prop", help="Property to visualize")
    parser.add_argument("-c", "--color_hops", help="Color hops", action="store_true")
    parser.add_argument("-m", "--map", help="Visualize world map", action="store_true")
    parser.add_argument("-s", "--show", help="Show graph", action="store_true")
    parser.add_argument("-o", "--output", help="Output graph file", action="store_true")
    args = parser.parse_args(args)
    from ip_analysis_tool.util.graph_getter import get_graph_by_date
    g = get_graph_by_date(args.graph)
    if args.map:
        visualize_graph_map(g, args.name, color_hops=args.color_hops, show=args.show, save=args.output)
    else:
        visualize_graph(g, args.name, prop=args.prop, color_hops=args.color_hops)

if __name__ == "__main__":
    main()
