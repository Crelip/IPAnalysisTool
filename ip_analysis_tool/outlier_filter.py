# Filtering out outliers from the data
import pandas as pd
import numpy as np

def remove_empty_dates(data):
    """
    Removes dates from the data that have no data.
    :param data: Data to filter
    :return: Filtered data
    """
    return data[data["num_vertices"] != 0]

def z_score_filter(data, key=None, threshold=3):
    """
    Filters out outliers from the data using the z-score method.
    :param data: Data to filter
    :param key: Column to filter on
    :param threshold: Threshold for filtering outliers
    :return: Filtered data
    """
    from scipy.stats import zscore
    data["zscore"] = zscore(data[key])
    return data[np.abs(data["zscore"]) < threshold]

def iqr_filter(data, key=None, threshold=1.5):
    """
    Filters out outliers from the data using the IQR method.
    :param data: Data to filter
    :param key: Column to filter on
    :param threshold: Threshold for filtering outliers, should not be set to other than 1.5
    :return: Filtered data
    """
    q1 = data[key].quantile(0.25)
    q3 = data[key].quantile(0.75)
    iqr = q3 - q1
    return data[(data[key] >= q1 - threshold * iqr) & (data[key] <= q3 + threshold * iqr)]

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-f", "--filename", help="CSV file to read data from")
    parser.add_argument("-k", "--key", help="Column to filter on")
    parser.add_argument("-m", "--method", help="Method to use for filtering")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-t", "--threshold", type=int, help="Threshold for filtering outliers")
    args = parser.parse_args()
    data = pd.read_csv(args.filename)
    filtered = pd.DataFrame()
    if args.method == "zscore":
        filtered = z_score_filter(data, args.key, args.threshold)
    elif args.method == "iqr":
        filtered = iqr_filter(data, args.key, args.threshold)
    filtered.to_csv(args.output, index=False)

if __name__ == "__main__":
    main()