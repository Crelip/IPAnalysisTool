def visualize_chart(data, x_characteristic, y_characteristic, x_label, y_label, title):
    import matplotlib.pyplot as plt
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data[x_characteristic], data[y_characteristic], marker="o", linestyle="-")
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
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