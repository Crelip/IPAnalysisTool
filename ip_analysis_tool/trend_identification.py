import pandas as pd
import numpy as np
from pandas import DataFrame
from typing import Tuple


def linear_regression(
        data: DataFrame,
        x_characteristic: str,
        y_characteristic: str):
    """
    Perform linear regression on time series data.
    :param data: The time series data to analyze.
    :param x_characteristic: The column name of the data to analyze for the x-axis.
    :param y_characteristic: The column name of the data to analyze for the y-axis.
    :return: DataFrame with original values + trend column.
    """
    from sklearn.linear_model import LinearRegression

    data = data[data["num_vertices"] != 0]
    data = data.reset_index(drop=True)
    if x_characteristic == "" or x_characteristic is None or x_characteristic == "date":
        data["date"] = pd.to_datetime(data["date"])
        data["date_ordinal"] = data["date"].map(pd.Timestamp.toordinal)
        x = data[["date_ordinal"]]
    else:
        x = data[x_characteristic].values

    y = data[y_characteristic].values

    model = LinearRegression()
    model.fit(x, y)

    # add trend for historical data
    data["fit"] = model.predict(x)

    # cleanup
    data = data.drop(columns=["date_ordinal"])
    return data


def gaussian_fit(
        data: DataFrame,
        x_characteristic: str,
        y_characteristic: str
) -> Tuple[DataFrame, float, float]:
    """
    Perform Gaussian fit on time series data.
    :param data: The time series data to analyze.
    :param y_characteristic: The column name of the data to analyze.
    :return: DataFrame with original values and smoothed values.
    """
    import math
    output = data.copy()

    x = data[x_characteristic].tolist()
    y = data[y_characteristic].tolist()

    total_count = sum(y)
    probs = [c / total_count for c in y]
    mean = sum(d * pr for d, pr in zip(x, probs))
    variance = sum(pr * (d - mean) ** 2 for d, pr in zip(x, probs))
    std = math.sqrt(variance)
    gauss = [
        1 / (std * math.sqrt(2 * math.pi))
        * math.exp(-0.5 * ((d - mean) / std) ** 2)
        * total_count
        for d in x]

    output["gaussian_fit"] = gauss
    return output, mean, std


def poisson_fit(
        data: DataFrame,
        x_characteristic: str,
        y_characteristic: str,
) -> Tuple[pd.DataFrame, float, float]:
    """
    Perform Poisson approximation on time series data.
    :param data: The DataFrame containing your series.
    :param x_characteristic: Name of the column holding the discrete x‐values (e.g. hop distance).
    :param y_characteristic: Name of the column holding counts at each x.
    :return: Either
        - output_df with a new 'poisson_fit' column, or
        - (output_df, lambda) if return_lambda=True.
    """
    import math
    output = data.copy()

    x = data[x_characteristic].tolist()
    y = data[y_characteristic].tolist()

    # Total number of items and mean (lambda) of the distribution
    total_count = sum(y)
    mean = sum(d * c for d, c in zip(x, y)) / total_count

    # Poisson fit: P(X = d) = e^{–lambda} λ^d / d! => expected count = total_count * P(X = d)
    poisson = [
        total_count * math.exp(-mean) * (mean ** d) / math.factorial(int(d))
        for d in x
    ]

    output["poisson_fit"] = poisson
    return output, mean, math.sqrt(mean)


methods_map = {
    "linreg": {
        "name": "Linear Regression",
        "method": linear_regression,
    },
    "gaussian": {
        "name": "Gaussian Fit",
        "method": gaussian_fit,
    },
    "poisson": {
        "name": "Poisson Fit",
        "method": poisson_fit,
    },
}


def trend_identification(
        filename: str,
        y_characteristic: str,
        x_characteristic: str = None,
        method: str = "linreg",
        impute: bool = False):
    data = pd.read_csv(filename)
    data["date"] = pd.to_datetime(data["date"])
    # Clean/impute missing weeks
    if impute:
       # Find rows where numVertices is 0
        zero_rows = data['numVertices'] == 0
        # Replace all values in those rows with NaN
        data.loc[zero_rows, :] = np.nan
        # Forward fill to impute missing values
        data.ffill(inplace=True)
    else:
        data = data[data['numVertices'] != 0].copy()

    entry = methods_map.get(method)
    if entry is None:
        raise ValueError(f"Invalid method: {method}")

    result = entry["method"](
        data,
        x_characteristic=x_characteristic,
        y_characteristic=y_characteristic
    ) if method == "linreg" else (
        entry["method"](
            data,
            x_characteristic=x_characteristic,
            y_characteristic=y_characteristic
        )[0]
    )


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        "-f",
        "--filename",
        help="Generates data from the file containing the given filename.")
    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbose output.",
        action="store_true")
    parser.add_argument(
        "-m",
        "--method",
        help="Method to use to identify trends")
    parser.add_argument(
        "-i",
        "--impute",
        help="Impute gaps",
        action="store_true")
    parser.add_argument(
        "-p",
        "--plot",
        help="Plot trends",
        action="store_true")
    parser.add_argument(
        "-x",
        "--x_characteristic",
        help="X characteristic to use for trend identification")
    parser.add_argument(
        "-y",
        "--y_characteristic",
        help="Y characteristic to use for trend identification")
    parser.add_argument("-t", "--title", help="Title of the plot")
    parser.add_argument("-o", "--output", help="Output filename")
    parser.add_argument(
        "-s",
        "--save",
        help="Save the output to a file",
        action="store_true")
    parser.add_argument()
    args = parser.parse_args()
    data = trend_identification(
        args.filename,
        args.y_characteristic,
        args.x_characteristic,
        args.method,
        args.impute)

    if args.plot():
        from ip_analysis_tool.visualize.chart import visualize_chart_add_line
        visualize_chart_add_line(
            data=data,
            x_characteristic=args.x_characteristic,
            y_characteristic=args.y_characteristic,
            trend_characteristic="fit",
            title=args.title,
            filename=args.output if args.output else "",
            show=True,
            save=args.save)


if __name__ == "__main__":
    main()
