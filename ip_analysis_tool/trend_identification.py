import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame


def linear_regression(data: DataFrame, key_name="network_diameter"):
        """
        Perform linear regression on time series data.
        :param data: The time series data to analyze.
        :param key_name: The column name of the data to analyze.
        :return: DataFrame with original values, trend column and future predictions if any.
        """
        from sklearn.linear_model import LinearRegression

        data = data[data["num_vertices"] != 0]
        data = data.reset_index(drop=True)
        data["date"] = pd.to_datetime(data["date"])
        data["date_ordinal"] = data["date"].map(pd.Timestamp.toordinal)

        x = data[["date_ordinal"]]
        y = data[key_name].values

        model = LinearRegression()
        model.fit(x, y)

        # add trend for historical data
        data["trend"] = model.predict(x)

        # cleanup
        data = data.drop(columns=["date_ordinal"])
        return data


def gaussian_fit(data: DataFrame, x_characteristic : str, y_characteristic: str = "network_diameter"):
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
    variance = sum(pr * (d - mean) ** 2 for d, pr in zip (x, probs))
    std = math.sqrt(variance)
    gauss = [
        1 / (std * math.sqrt(2 * math.pi))
        * math.exp(-0.5 * ((d - mean) / std) ** 2)
        * total_count
        for d in x]

    output["gauss_fit"] = gauss
    return output

def poisson_fit(data: DataFrame, x_characteristic: str, y_characteristic: str = "network_diameter"):
    """
    Perform Poisson approximation on time series data.
    :param data: The DataFrame containing your series.
    :param x_characteristic: Name of the column holding the discrete x‐values (e.g. hop distance).
    :param y_characteristic: Name of the column holding counts at each x.
    :return: A new DataFrame with an added 'poisson_fit' column of expected counts.
    """
    import math
    output = data.copy()

    x = data[x_characteristic].tolist()
    y = data[y_characteristic].tolist()

    # Total number of items and mean (λ) of the distribution
    total_count = sum(y)
    lambda_ = sum(d * c for d, c in zip(x, y)) / total_count

    # Poisson fit: P(X = d) = e^{–λ} λ^d / d! ⇒ expected count = total_count * P(X = d)
    poisson = [
        total_count * math.exp(-lambda_) * (lambda_ ** d) / math.factorial(int(d))
        for d in x
    ]

    output["poisson_fit"] = poisson
    return output

def trend_identification(filename, verbose=False, method="linreg", impute = False):
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
    else: data = data[data['numVertices'] != 0].copy()
    # visualizeChart(data, "date", "networkDiameter", "Date", "Network Diameter", "Network Diameter Over Time")
    if method == "linreg" or method == "linearRegression" : linear_regression(data)
    #elif method == "linapp" or method == "linearApproximation": linearApproximation(data, verbose=verbose)
    else:
        raise ValueError(f"Invalid method: {method}")


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-f", "--filename", help="Generates data from the file containing the given filename.")
    parser.add_argument("-v", "--verbose", help="Verbose output.", action="store_true")
    parser.add_argument("-m", "--method", help="Method to use to identify trends")
    parser.add_argument("-i", "--impute", help="Impute gaps", action="store_true")
    parser.add_argument("-p", "--plot", help="Plot trends", action="store_true")
    args = parser.parse_args()
    trend_identification(args.filename, args.verbose, args.method, args.impute)

if __name__ == "__main__":
    main()