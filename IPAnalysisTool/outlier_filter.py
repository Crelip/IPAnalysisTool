# Filtering out outliers from the data
import pandas as pd
import numpy as np

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

def mad_filter(data, key=None, threshold=3.5):
    """
    Filters out outliers from the data using the MAD (Median Absolute Deviation) method.
    :param data: Data to filter
    :param key: Column to filter on
    :param threshold: Threshold for filtering outliers
    :return: Filtered data
    """
    median = data[key].median()
    mad = np.abs(data[key] - median).median()
    return data[np.abs(data[key] - median) / mad < threshold]

def resid_filter(data, key=None, threshold=2):
    """
    Filters out outliers from the data using the residuals method.
    :param data: Data to filter
    :param key: Column to filter on
    :param threshold: Threshold for filtering outliers
    :return: Filtered data
    """
    import statsmodels.api as sm
    data["weekNum"] = data["date"].map(pd.Timestamp.toordinal)
    x = sm.add_constant(data["weekNum"])
    model = sm.OLS(data[key], x).fit()
    residuals = model.resid
    threshold *= residuals.std()
    return data[np.abs(residuals) < threshold]

def isolation_forest_filter(data, key=None, threshold=0.05):
    """
    Filters out outliers from the data using the Isolation Forest method.
    :param data: Data to filter
    :param key: Column to filter on
    :param threshold: Threshold for filtering outliers
    :return: Filtered data
    """
    from sklearn.ensemble import IsolationForest
    model = IsolationForest(contamination=threshold)
    data["anomaly"] = model.fit_predict(data[key])
    return data[data["anomaly"] == 1]

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
    elif args.method == "mad":
        filtered = mad_filter(data, args.key, args.threshold)
    elif args.method == "resid":
        filtered = resid_filter(data, args.key, args.threshold)
    elif args.method == "isolation":
        filtered = isolation_forest_filter(data, args.key, args.threshold)
    filtered.to_csv(args.output, index=False)

if __name__ == "__main__":
    main()