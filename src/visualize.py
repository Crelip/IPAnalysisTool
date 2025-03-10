import graph_tool.all as gt
import pandas as pd
import matplotlib.pyplot as plt
def baseVisualize(g: gt.Graph, name: str):
    gt.graph_draw(g,
            gt.sfdp_layout(g),
            output_size=(10000,10000),
            vertex_text=g.vp.ip,
            vertex_font_size=8,
            vertex_size=6,
            edge_pen_width=2.0,
            bg_color=[1,1,1,1],
            output=f"scratchpad/{name}.png"
                  )

def visualizeChart(data, xCharacteristic, yCharacteristic, xLabel, yLabel, title):
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