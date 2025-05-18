from pandas import DataFrame
def visualize_chart(data: DataFrame,
                    y_characteristic: str,
                    title: str,
                    x_characteristic: str = "date",
                    x_label: str = None,
                    y_label: str = None,
                    ):
    """
    Visualize a chart with zoom functionality.

    :param data: The input data as a pandas DataFrame.
    :param y_characteristic: The column name in the DataFrame to use for the y-axis.
    :param title: The title of the chart.
    :param x_characteristic: The column name in the DataFrame to use for the x-axis. Defaults to "date".
    :param x_label: The label for the x-axis. If None, it will be set to the same value as x_characteristic.
    :param y_label: The label for the y-axis. If None, it will be set to the same value as y_characteristic.
    :return: None
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    # Fill missing arguments
    if x_characteristic not in data.columns:
        print("x_characteristic is not in columns, please check your input.")
        return
    if y_characteristic not in data.columns:
        print("y_characteristic is not in columns, please check your input.")
        return
    if x_label is None:
        x_label = x_characteristic
    if y_label is None:
        y_label = y_characteristic
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data[x_characteristic], data[y_characteristic], marker="o", linestyle="")
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if x_characteristic == "date":
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
    plt.tight_layout()

    # Zoom functionality (e.g. if not using Jupyter in order to use the scroll wheel)
    def zoom_fun(event):
        base_scale = 1.1
        cur_ylim = ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return

        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            scale_factor = 1
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        plt.draw()

    fig.canvas.mpl_connect('scroll_event', zoom_fun)
    plt.show()

def visualize_chart_dual(data: DataFrame,
                         y_characteristic: str,
                         title: str,
                         x_characteristic: str = "date",
                         y_2_characteristic: str = "trend",
                         x_label: str = None,
                         y_label: str = None,
                         y_2_label: str = None,
                         ):
    """
    Visualize a line chart with zoom functionality.
    :param data: The input data as a pandas DataFrame.
    :param y_characteristic: The column name in the DataFrame to use for the y-axis.
    :param y_2_characteristic: The column name in the DataFrame to use for the 2nd y-axis parameter.
    :param title: The title of the chart.
    :param x_characteristic: The column name in the DataFrame to use for the x-axis. Defaults to "date".
    :param x_label: The label for the x-axis. If None, it will be set to the same value as x_characteristic.
    :param y_label: The label for the y-axis. If None, it will be set to the same value as y_characteristic.
    :param y_2_label: The label for the 2nd y-axis parameter. If None, it will be set to the same value as y_2_characteristic.
    :return: None
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    # Fill missing arguments
    if x_label is None:
        x_label = x_characteristic
    if y_label is None:
        y_label = y_characteristic
    if y_2_label is None:
        y_2_label = y_2_characteristic

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data[x_characteristic], data[y_characteristic], marker="o", linestyle="", label=y_label)
    ax.plot(data[x_characteristic], data[y_2_characteristic], marker="o", linestyle="", color="red", label=y_2_label)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label + ", " + y_2_label)
    ax.set_title(title)
    if x_characteristic == "date":
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
    plt.tight_layout()

    # Zoom functionality
    def zoom_fun(event):
        base_scale = 1.1
        cur_ylim = ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return

        if event.button == "up":
            scale_factor = 1 / base_scale
        elif event.button == "down":
            scale_factor = base_scale
        else:
            scale_factor = 1
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        plt.draw()

    fig.canvas.mpl_connect("scroll_event", zoom_fun)
    plt.legend()
    plt.show()

def visualize_chart_add_line(data: DataFrame,
                    y_characteristic: str,
                    title: str,
                    x_characteristic: str = "date",
                    y_line_characteristic: str = "trend",
                    x_label: str = None,
                    y_label: str = None,
                    y_line_label: str = None,
                    ):
    """
    Visualize a line chart with zoom functionality.
    :param data: The input data as a pandas DataFrame.
    :param y_characteristic: The column name in the DataFrame to use for the y-axis.
    :param y_line_characteristic: The column name in the DataFrame to use for the y-axis line.
    :param title: The title of the chart.
    :param x_characteristic: The column name in the DataFrame to use for the x-axis. Defaults to "date".
    :param x_label: The label for the x-axis. If None, it will be set to the same value as x_characteristic.
    :param y_label: The label for the y-axis. If None, it will be set to the same value as y_characteristic.
    :param y_line_label: The label for the y-axis line. If None, it will be set to the same value as y_line_characteristic.
    :return: None
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    # Fill missing arguments
    if x_label is None:
        x_label = x_characteristic
    if y_label is None:
        y_label = y_characteristic
    if y_line_label is None:
        y_line_label = y_line_characteristic

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data[x_characteristic], data[y_characteristic], marker="o", linestyle="", label=y_label)
    ax.plot(data[x_characteristic], data[y_line_characteristic], color="red", linestyle="-", label=y_line_label)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if x_characteristic == "date":
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
    plt.tight_layout()

    # Zoom functionality
    def zoom_fun(event):
        base_scale = 1.1
        cur_ylim = ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return

        if event.button == "up":
            scale_factor = 1 / base_scale
        elif event.button == "down":
            scale_factor = base_scale
        else:
            scale_factor = 1
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        plt.draw()

    fig.canvas.mpl_connect("scroll_event", zoom_fun)
    plt.legend()
    plt.show()

def visualize_chart_add_dual_line(data: DataFrame,
                    y_characteristic: str,
                    title: str,
                    x_characteristic: str = "date",
                    y_line_characteristic: str = "trend",
                    y_2_line_characteristic: str = "trend",
                    x_label: str = None,
                    y_label: str = None,
                    y_line_label: str = None,
                    y_2_line_label: str = None
                    ):
    """
    Visualize a line chart with zoom functionality.
    :param data: The input data as a pandas DataFrame.
    :param y_characteristic: The column name in the DataFrame to use for the y-axis.
    :param y_line_characteristic: The column name in the DataFrame to use for the y-axis line.
    :param title: The title of the chart.
    :param x_characteristic: The column name in the DataFrame to use for the x-axis. Defaults to "date".
    :param x_label: The label for the x-axis. If None, it will be set to the same value as x_characteristic.
    :param y_label: The label for the y-axis. If None, it will be set to the same value as y_characteristic.
    :param y_line_label: The label for the y-axis line. If None, it will be set to the same value as y_line_characteristic.
    :return: None
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    # Fill missing arguments
    if x_label is None:
        x_label = x_characteristic
    if y_label is None:
        y_label = y_characteristic
    if y_line_label is None:
        y_line_label = y_line_characteristic
    if y_2_line_label is None:
        y_2_line_label = y_2_line_characteristic

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data[x_characteristic], data[y_characteristic], marker="o", linestyle="", label=y_label)
    ax.plot(data[x_characteristic], data[y_line_characteristic], color="red", linestyle="-", label=y_line_label)
    ax.plot(data[x_characteristic], data[y_2_line_characteristic], color="green", linestyle="-", label=y_2_line_label)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if x_characteristic == "date":
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
    plt.tight_layout()

    # Zoom functionality
    def zoom_fun(event):
        base_scale = 1.1
        cur_ylim = ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return

        if event.button == "up":
            scale_factor = 1 / base_scale
        elif event.button == "down":
            scale_factor = base_scale
        else:
            scale_factor = 1
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        plt.draw()

    fig.canvas.mpl_connect("scroll_event", zoom_fun)
    plt.legend()
    plt.show()