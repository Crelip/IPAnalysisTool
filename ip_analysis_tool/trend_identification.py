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
    :return: DataFrame with original values with a new 'fit' column.
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
    :return: DataFrame with original values with a new 'gaussian_fit' column and mean and standard deviation values as a float.
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
    :return: DataFrame with original values with a new 'poisson_fit' column and mean and standard deviation values as a float.
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
