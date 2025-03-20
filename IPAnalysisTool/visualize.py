from graph_tool import Graph
def visualize_graph(g: Graph, name: str, prop: str = "ip"):
    from graph_tool.all import graph_draw, sfdp_layout
    graph_draw(
            g,
            sfdp_layout(g),
            output_size=(10000,10000),
            vertex_text=g.vertex_index if prop== "vertex_index" else g.vp[prop],
            vertex_font_size=8,
            vertex_size=6,
            edge_pen_width=2.0,
            bg_color=[1,1,1,1],
            output=f"scratchpad/{name}.svg"
                  )

def visualize_graph_world(g: Graph, name: str, prop: str = "ip", geo_data = None):
    from graph_tool.all import graph_draw, group_vector_property
    from mpl_toolkits.basemap import Basemap
    import matplotlib.pyplot as plt
    import graph_tool.all as gt
    if geo_data is None:
        from IPAnalysisTool.util.geoDataUtil import get_geo_data
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

    pos = gt.group_vector_property([lon, lat])

    m = Basemap(
        projection="merc",
        resolution="l",
        llcrnrlat=-60,
        urcrnrlat=80,
        llcrnrlon=-180,
        urcrnrlon=180,
    )

    m.shadedrelief(scale=.2)

    a = graph_draw(g, pos=pos.t(lambda x: m(*x)),  # project positions
                      edge_color=(.1, .1, .1, .1), mplfig=ax)

    a.fit_view()
    a.set_zorder(10)
    plt.tight_layout()
    plt.show()
    fig.savefig(f"scratchpad/{name}.svg")

def visualizeChart(data, xCharacteristic, yCharacteristic, xLabel, yLabel, title):
    import matplotlib.pyplot as plt
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data[xCharacteristic], data[yCharacteristic], marker="o", linestyle="-")
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)
    ax.set_title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()

    def zoom_fun(event):
        base_scale = 1.1  # adjust this value for faster/slower zooming
        cur_ylim = ax.get_ylim()
        xdata = event.xdata  # get event x location in data coordinates
        ydata = event.ydata  # get event y location in data coordinates
        if xdata is None or ydata is None:
            return
        # Determine zoom direction
        if event.button == 'up':  # scroll up to zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':  # scroll down to zoom out
            scale_factor = base_scale
        else:
            scale_factor = 1
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        plt.draw()

    # Connect the scroll event to the zoom function
    fig.canvas.mpl_connect('scroll_event', zoom_fun)
    plt.show()